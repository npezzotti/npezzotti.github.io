Title: How to deploy an Nginx server on AWS EC2 with Terraform
Date: 2022-08-19
Author: Nathan Pezzotti
Category: devops
Tags: terraform, aws, devops
Image: nginx-logo.png

In this tutprial, we will use Terraform to create a VPC with a single public subnet in which we will launch an EC2 instance running Nginx.

By the end of this, you will have learned the following:

* Basic understanding of Terraform and usage
* Familiary with the following AWS Services:
    * VPC
    * Subnets
    * Security Groups
    * AMI
    * EC2

## Getting Started
### What is Terraform?

Terraform is an infrastructure as code tool. Infastructure as code tools allow you to programmatically spin up resources such as EC2s, Azure VMs, etc. through code. In Terraform, this code is called HCL (Hashicorp configuration language). The language is declaritive, meaning it describes the state of your infrastructure and leaves the details of arriving at that state up to Terraform.

### Terraform Setup
####  Install Terraform
Refer to the official documentation on installing Terraform [here](https://learn.hashicorp.com/tutorials/terraform/install-cli), where you can find dedicated instructions for MacOS, Windows, different Linux distributions, and a manual method.

#### Terraform module
Create a directory to hold the files for your project and change into the directory:
```
$ mkdir terraform-ec2-nginx && cd terraform-ec2-nginx
```
Run the following command to create the main file for our module:
```
$ touch main.tf
```
In the `main.tf` add the following code:
```
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}
```
This code creates a `terraform` block, where you configure Terraform settings. In this block, we are adding a version constraint for Terraform with the `required_version` directive, and defining the required providers (`aws`) with their source address and version constraints. 

Terraform providers are plugins which work with a related set of resources/APIs, such as those exposed by cloud providers like AWS, GCP or Azure. In this project, we will use the `hashicorp/aws` provider to spin up AWS resources. Authentication to AWS can be configured in multiple ways in this provider, though we rely on shared configuration files in this tutorial, which requires you [install and configure the AWS CLI on your local machine with access keys](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html). Access keys allow programmatic access to the AWS API and are associated to a particular IAM user. For more information on creating an access key, see the [AWS documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey). The `aws` provider will souce the default credentials in `$HOME/.aws/config` and `$HOME/.aws/credentials` on Linux and macOS, and `"%USERPROFILE%\.aws\config"` and `"%USERPROFILE%\.aws\credentials"` on Windows.

Alternatively, you can skip configuring the AWS CLI and configure the provider with environment variables:
```
$ export AWS_ACCESS_KEY_ID="ACCESS_KEY"
$ export AWS_SECRET_ACCESS_KEY="SECRET_KEY"
```

### Create AWS Resources

Below the `terraform` block, add the following code:
```
provider "aws" {
  region = var.aws_region
}
```
`provider` blocks are where you configure the provider you are using. In the code above, we are setting the AWS region in which we'll be creating these resource.

In the above code, we are referencing a Terraform variable, which we will create next. A Terraform variable is a static value which can be set in one place and referenced throughout your module.

Create a `variables.tf` file in this directory:
```
$  touch variables.tf
```
Add the following content:
```
variable "aws_region" {
  type        = string
  description = "AWS region"
  default     = "us-east-1"
}
```
In this code we are defining our input variable within a `variable` block. The variable will be a string and will have a default value of `us-east-1`. If we'd like to override these defaults, we can do so later when running `terraform apply` by usin the `-var` flag. 

Let's also add a variable for our project name, which we can reference when defining metadata on resources, and an availability zone:
```
variable "project-name" {
  type        = string
  description = "Name of the project"
  default     = "tf-nginx"
}

variable "tf-nginx-az" {
  type        = string
  description = "Availability zone"
  default     = "us-east-1a"
}
```
The first resource we need to create is a VPC. A VPC is a virtual network which is unique to your AWS account and is logically isolated from other virtual networks.

Add the following code to the `main.tf` file:
```
resource "aws_vpc" "tf-nginx-vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project-name}-vpc"
  }
}
```
This code uses the `aws_vpc` resource to create a VPC with a `10.0.0.0/16` IPv4 CIDR block and support for assigning a public DNS name to all EC2s created within it.

To allow resources in our VPC to have access the internet, we need to create an internet gateway and attach it to the VPC.

```
resource "aws_internet_gateway" "tf-nginx-igw" {
  vpc_id = aws_vpc.tf-nginx-vpc.id

  tags = {
    Name = "${var.project-name}-igw"
  }
}
```

By default, each VPC comes with a single route table configured with a local route. In order to route traffic between the internet and our EC2, we need to configure a route table with a route for any public traffic.

Add the following code in the `main.tf`:
```
resource "aws_route_table" "tf-nginx-pulic-rt" {
  vpc_id = aws_vpc.tf-nginx-vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.tf-nginx-igw.id
  }

  tags = {
    Name = "${var.project-name}-public-route-table"
  }
}
```
Next, we will create a dedicated subnet in which we will deploy the EC2. A subnet is a range of IP addresses within a VPC which are created in a single availability zone and in which you can launch your AWS resources.

Add the following code to the `main-tf`:
```
resource "aws_subnet" "tf-nginx-subnet" {
  vpc_id                  = aws_vpc.tf-nginx-vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = var.tf-nginx-az
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project-name}-subnet"
  }
}
```
Here we have specified the VPC and availability zone in which we will create this subnet as well as an IPv4 CIDR block. Important to note is that we are setting `map_public_ip_on_launch` to `true`, which will allow instances created in this subnet to be created with a public IP address, which we will later use to access the Nginx site. 

We will also need to associate our subnet to the public route table we defined previously so that traffic from that subnet is routed to the internet gateway- add the following code to create a subnet association between our public route table and subnet:
```
resource "aws_route_table_association" "tf-nginx-subnet-rt-association" {
  subnet_id      = aws_subnet.tf-nginx-subnet.id
  route_table_id = aws_route_table.tf-nginx-pulic-rt.id
}
```
Now we will create a security group for the EC2. A security group is like a virtual firewall which acts at the EC2 instance level- it allows us to control the traffic that is allowed in and out of the resources that it is associated with.

Add the following code in the `main.tf` file:
```
resource "aws_security_group" "tf-nginx-sg" {
  name   = "${var.project-name}-sg"
  vpc_id = aws_vpc.tf-nginx-vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 0
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```
In this code, we used the `aws_security_group` resource to define a security group named `tf-nginx-sg` in our `tf-nginx-vpc`. We also defined two ingress rules which retrict all inbound TCP traffic to port 80 (for Nginx) and 22 (for SSH) from any IPv4 address. Additionally, we defined an egress rule which allows any outbound traffic from the EC2, by setting the `protocol` to `-1` and the ports to`0`.

Lastly, we will define the EC2 instance:
```
resource "aws_instance" "tf-nginx-server" {
  ami                         = var.ami
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.tf-nginx-subnet.id
  vpc_security_group_ids      = [aws_security_group.tf-nginx-sg.id]
  user_data                   = file("scripts/nginx.sh")
  user_data_replace_on_change = true

  tags = {
    Name = var.instance_name
  }
}
```
In this code, we are specifying the EC2's Amazon machine image, type, and name (all input variables we will define in the next step), the subnet it should be created, and a list of security groups which should be attached. We are also adding a user-data script, which we will create in an upcoming step and enabling a setting that forces the re-creation of our EC2 if the script is altered.

In the `variables.tf` file, add the following variables used above for the AMI, the instance type, and the instance name:
```
variable "instance_name" {
  description = "Value of the Name of the EC2 instance"
  type        = string
  default     = "NginxServer"
}

variable "ami" {
  description = "AMI"
  type        = string
  default     = "ami-090fa75af13c156b4"
}

variable "instance_type" {
  description = "Instance type"
  type        = string
  default     = "t2.micro"
}
```
Now that the infrastructure is defined, we can turn our attention towards installing and configuring Nginx. To do this, we will create a [user data script](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html#user-data-shell-scripts). A user data script is a shell script which is run as the `root` user when an EC2 is initially created and allows you to apply some initial configuration to the server.

Run the following commands to create the directory and file for our provisioning script:
```
$  mkdir scripts && touch scripts/nginx.sh
```
Add the following content to the `scripts/nginx.sh`:
```
#! /bin/bash

set -e

echo  "Updating packages"
yum update -y

if [[ $(amazon-linux-extras list | grep nginx | awk '{ print $3 }') != 'enabled' ]] 
then
    echo "Enabling Nginx package"
    amazon-linux-extras enable nginx1
    yum clean metadata
fi

echo "Installing Nginx"
yum install -y nginx

if [[ $(systemctl is-active nginx) != "active" ]]
then
    echo "Starting service nginx"
    systemctl start nginx
else
    echo "Nginx service is running"
fi

if [[ $(systemctl is-enabled nginx) != "enabled" ]]
then
    echo "Enabling service nginx"
    systemctl enable nginx
fi
```

This shell script performs the following actions:

1. Enables the Nginx package in the amazon-linux-extras repository
1. Installs the Nginx package
1. Starts and enables the Nginx Systemd service

When the instance is provisioned, you can view the contents of `/var/log/cloud-init-output.log` on the EC2 instance to view output of the script and debug if necessary.

### Apply Configuration

Finally, we are ready to run this code and create the resources. Before doing so, create an `outputs.tf` file in the working directory with the following code:
```
$ touch ouputs.tf
```
```
output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.tf-nginx-server.public_ip
}
```
This code creates a Terraform [output variable](https://www.terraform.io/language/values/outputs), which allows the end user to access information about the provisioned resource. This variable returns the public IP address our EC2, which we will use to connect to the Nginx server.

Run the following command to initalize Terraform in the current working directory:
```
$  terraform init
```
Next, run `terraform plan`:
```
$  terraform plan
```
`terraform plan` will generate a plan of execution. Terraform will assess the current state of the resources to be created, identify any differences between the definition in your code and this state, and detail the changes it will make to these resources, without actually changing them. Since these are new resources, there is no existing state and Terraform is going to create all of them.

When you are ready to apply these changes, run the following command to execute the plan:
```
$ terraform apply
```
When the command returns, you should be able to access the new EC2 at its public IP address and view the default Nginx site. Note the output variable we configured, which should be printed to the console when the command finishes. You can also print the outputs by running `terraform output`.

Finally, run the following command to open the UR in your browser to view the Nginx default site:
```
$ open "http://$(terraform output -raw instance_public_ip)"
```

### Clean Up

To delete all managed resources, run the following command:
```
$ terraform destroy
```