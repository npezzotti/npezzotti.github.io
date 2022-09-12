Title: Configure an HTTPS Apache Site with Custom Root CA on Ubuntu 20.04
Date: 2022-09-04
Author: Nathan Pezzotti
Category: networking
Tags: networking, linux
Image: https.jpg

## Overview
This tutorial demonstrates how to set up an HTTPS site on an Apache using a custom root CA. It is  the purpose of exploring how HTTPS works.

For this project, I used Ubuntu 20.04 and ran the command as a non-root user with sudo privileges.

### Install Apache and Configure the Default Site:
Begin by installing Apache, which is the web server we will use to configure this HTTPS site:
```
$ sudo apt update && sudo apt install apache2
```
We'll use the default `000-default`, which Apache creates by default and which is already enabled. To see enabled sites, you can run `a2query -s`:
```
$ a2query -s
000-default (enabled by site administrator)
``` 
View the site's configuration file at `/etc/apache2/sites-available/000-default.conf`. The `DocumentRoot` directive is set to `/var/www/html`, which means it will serve the content of that directory. Nothing needs to be changed in this file for the purpose of this tutorial, however we will modify the content in the `/var/www/html/index.html` file. You can do that with the following command:
```
$ sudo bash -c 'echo "This is served over HTTPS!" > /var/www/html/index.html'
```
The site is currently listening on port `80` and you can `curl` the site to see the content:
```
$ curl http://localhost
This is served over HTTPS!
```
This is, of course, not currently being served of HTTPS at the moment, so that is what we will configure next. 

### Configure TLS

To configure TLS, enable the `ssl` module in Apache, which provides TLS support:
```
$ sudo a2enmod ssl
```
A default Apache vhost configured to handle HTTPS traffic is created for you upon installation. Enable the `default-ssl` virtual host with the following command:
```
$ sudo a2ensite default-ssl
```
The `default-ssl` site basically handles all traffic to the server on port `443` if it is not previously matched by another virtual host. Inspect the `/etc/apache2/sites-available/default-ssl.conf` configuration to see the certificates and keys being used. Note that it will also serve the content of the `/var/www/html` directory.
```
<IfModule mod_ssl.c>
    <VirtualHost _default_:443>
    ...
    DocumentRoot /var/www/html
    ...
    SSLEngine on
    SSLCertificateFile      /etc/ssl/certs/ssl-cert-snakeoil.pem
    SSLCertificateKeyFile /etc/ssl/private/ssl-cert-snakeoil.key
    ...
    </VirtualHost>
</IfModule>
```
The `ssl-cert-snakeoil.pem` is a self-signed certificate and is created on install. It can be used for testing HTTPS, however we will configure our own certificates shortly. You can view the content of the default certificate with the following command:
```
$ openssl x509 -in /etc/ssl/certs/ssl-cert-snakeoil.pem -text
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number:
            59:9b:4e:dc:97:ff:98:e0:ea:7d:40:ea:ee:8e:57:ed:68:30:06:1c
        Signature Algorithm: sha256WithRSAEncryption
        Issuer: CN = ubuntu.vm
        Validity
            Not Before: Sep 10 16:29:57 2022 GMT
            Not After : Sep  7 16:29:57 2032 GMT
        Subject: CN = ubuntu.vm
        (truncated)
```
Note that the `Issuer` and `Subject` are the same, meaning it is a self-signed certificate.

Now that the `ssl` module and the `default-ssl` site are enabled, reload Apache to account for the changes:
```
$ sudo systemctl reload apache2
```
Now we can test the HTTPS site using `curl`. The `CN` on the `ssl-cert-snakeoil.pem` certificate should be the FQDN of your server- it is important that the `CN` or `Subject Alternate Name` on the certificate match the URL, or curl will fail to verify the certificate. You can run the following commands to extract it as a shell variable and use it to connect to the site over HTTPS:
```
$ HOST=$(openssl x509 -in /etc/ssl/certs/ssl-cert-snakeoil.pem -text | grep "Subject: CN" | awk '{print $4}')
$ curl --cacert /etc/ssl/certs/ssl-cert-snakeoil.pem https://$HOST
This is served over HTTPS!
```
If the DNS name does not resolve, try using the `--resolve` option with curl, which allows you to map that hostname to localhost:
```
$ curl --cacert /etc/ssl/certs/ssl-cert-snakeoil.pem --resolve $HOST:443:127.0.0.1 https://$HOST
This is served over HTTPS!
```
Note, in both commands, we used the `--cacert` flag to specify the certificate file `curl` should use to verify the peer, since this is a self-signed certificate, and isn't used by default. Were we to omit this, `curl` would fail with a "unknown CA" error. If you want to avoid having to do this, you can install add the self-singed certificate to the trusted certificates on the system by running the following commands:

```
$ sudo apt-get install -y ca-certificates
$ sudo /etc/ssl/certs/ssl-cert-snakeoil.pem /usr/local/share/ca-certificates/ssl-cert-snakeoil.crt
$ sudo update-ca-certificates
```
This is useful for understanding how you might configure and connect over HTTPS using self-signed certificates. However, PKIs often use a RootCA as a trusted third party- the next section shows how to set up a working example of that.

### Create Custom Root CA
First, make a directory where we will store these files in your home directory and change into it. 
```
mkdir ~/certs && cd certs
```
Generate a root CA private key:
```
$ openssl genrsa -out rootCAKey.pem 2048
```
Create a self-signed root certificate using that key- you will be asked several questions which determine the information on the certificate and which can be whatever you'd like:
```
$ openssl req -x509 -sha256 -new -nodes -key rootCAKey.pem -days 3650 -out rootCACert.pem
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:US
State or Province Name (full name) [Some-State]:New York
Locality Name (eg, city) []:New York City
Organization Name (eg, company) [Internet Widgits Pty Ltd]:Some Organization
Organizational Unit Name (eg, section) []:
Common Name (e.g. server FQDN or YOUR name) []:someorganization.org
Email Address []:someone@someorganization.org
```
Next, we'll use the generated Root CA and key to sign a certificate used by our Apache server. Generate the private key for the Apache server with the following command:
```
$ openssl genrsa -out  my-apache-server.key 2048
```
In order for the CA sign the certificate, you musr present it with a certificate signing request. Run the following command to create this:
```
$ openssl req -new -key my-apache-server.key -out my-apache-server.csr
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:US
State or Province Name (full name) [Some-State]:New York
Locality Name (eg, city) []:New York City
Organization Name (eg, company) [Internet Widgits Pty Ltd]:Some Other Organization
Organizational Unit Name (eg, section) []:
Common Name (e.g. server FQDN or YOUR name) []:ubuntu.vm
Email Address []:someone@someotherorganization.org

Please enter the following 'extra' attributes
to be sent with your certificate request
A challenge password []:
An optional company name []:
```
Again, for the purpose of this tutorial, the organization information can be whatever you'd like. However since this is the certificate of the server to which we'll be connecting, ensure the `CN` is the DNS name of your server (i.e the $HOST variable from earlier).

Finally, sign the certificate using the root CA's certificate and private key.
```
$ openssl x509 -req -days 365 -in my-apache-server.csr -CA rootCACert.pem -CAkey rootCAKey.pem -CAcreateserial -out my-apache-server.crt
Signature ok
subject=C = US, ST = New York, L = New York City, O = Some Other Organization, CN = ubuntu.vm, emailAddress = someone@someotherorganization.org
Getting CA Private Key
```
Now that we have the server certificate and private key, modify the `/etc/apache2/sites-available/default-ssl.conf` to change the paths to point to these files:
```
SSLCertificateFile /home/<YOUR_USER>/certs/my-apache-server.crt
SSLCertificateKeyFile /home/<YOUR_USER>/certs/my-apache-server.key
```
Verify the syntax is okay and reload Apache:
```
$ sudo apachectl -t
Syntax OK
$ sudo systemctl reload apache2
```
Now, you can use the root CA certificate to verify the Apache server's certificate when connecting to the site:
```
$ curl --cacert ~/certs/rootCACert.pem https://$HOST
This is served over HTTPS!
```
As before, if you'd like to avoid having to use the `--cacert` flag, you can add the custom root certificate to the trusted certificates on the system. For a more detailed look at the certificate validation process, run curl with the `-v` flag.