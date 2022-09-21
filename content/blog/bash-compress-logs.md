Title: Bash Script to Compress Log Files
Date: 2022-09-17
Author: Nathan Pezzotti
Category: linux
Tags: linux, programming
Image: linux.jpg

This post shows an example of a bash script which compresses all files matching a pattern in a given directory. It can be used as a cron job or one-off to rotate growing log files on a server. The `logrotate` program is a better candidate for this in real world situations, but this was a fun exercise in scripting and could be useful in some scenarios.

```shell
#!/bin/bash

#################################################
# Compresses files over 10M in a given directory.
#################################################

set -e

display_usage() 
{
        echo "Usage: $(basename $0) <directory> [<file_pattern>]"
}

if [ $UID -ne 0 ]
then
    echo "This script must be run as root." >&2
    exit 1
fi

if [ $# -lt 1 ]
then
    display_usage
    exit 1
fi

DIR=$1
FILE_SIZE="10M"
PATTERN=$2

FILES=$(find ${DIR} -type f -size ${FILE_SIZE} -regex ${PATTERN:-.*\/.*\.log})

for file in ${FILES[@]}
do
    echo "$(date "+%F %T %Z"): compressing ${file}..."

    INDEX=1
    while [ -f ${file}.${INDEX}.gz ]
    do
        ((INDEX++))
    done

    gzip -k -S .${INDEX}.gz ${file}
    cat /dev/null > ${file}
done
```

### Explanation of code:

- *Line 1:* this is a shebang, which tells the kernel which program to use to execute the contents of the script- in this case, `/bin/bash`.
- *Lines 3-5:* a comment declaring the purpose of the script.
- *Line 7:* modifies the shell behavior to make sure the script exits if any command exits with an error.
- *Lines 9-12:* a bash function which prints instructions on using the script. The `echo` command prints the name of the script with arguments. `$0` returns the absolute path to the script. `basename` modifes this path so that only the file name is returned. This way, only the name of the file is printed no matter which directory the script is run from.
- *Lines 14-18:* check to see if the user executing the script is running it as root or with superuser privileges. To do this, we check if the `$UID` variable, a shell variable which stores the ID of the user, is equal to 0 (root user ID).
- *Lines 20-24:* check to see that the user supplied at least 1 argument- if not, display the usage and exit. `$#` is a shell variable which returns the number of arguments supplied to a script.
- *Line 26:* set a `DIR` variable as the first argument provided to the script. This is the directory where the script will look for files.
- *Line 27:* set a `FILE_SIZE` variable to 10 megabytes. The script will only compress files of that size or greater. This is a good size at which to rotate a file, but it can be adjusted if needed.
- *Line 28:* set a `PATTERN` variable as the second argument provided to the script. This is a shell pattern used to match the target files.
- *Line 30:* use the `find` utility to collect all files and save it as an array. The `$DIR` variable is provided as the first argument , the starting directory from which files will be recursively searched. The `-type f` argument indicates that the command should only look for files. `-size` constrains the command to only return files which a size greater than `$FILE_SIZE` (`10M`). The `-regex` argument takes a regex to further filter which files are returned. This uses a feature of brace expansion which sets a default value (`.*\/.*\.log`) assuming the user did not provide a second argument (and `$PATTERN` is empty). The full command is enclosed in parenthesis and a leading `$`, also know as command substitution, which will allow the output of the command to be saved in the variable.
- *Lines 32-44:* this is a bash for loop, used to iterate over the `$FILES` array (all the files returned by the find command). `${<ARRAY>[@]}` returns all values in the array.
- *Line 34:* print a log with the current date and time and which file is going to be compressed.
- *Lines 36-40:* this is a while loop in which we determine the name of the compressed file. The file name should be `<FILE_NAME>.<NUM_TIMES_COMPRESSED>.gz`. Assuming the file has already been compressed, we want the `<NUM_TIMES_COMPRESSED>` to increment. To do this we set an `INDEX` shell variable to 1 and add a  while loop condition which checks to see if a file exists with that index (i.e `<FILE_NAME>.1.gz`). If it does, the value of `INDEX` is incremented and the while condition is run again. This code will continue to run until a file with that name does not exist.
- *Line 42:* compress the file with gzip. The `-k` option keeps the original file, which would be deleted by default. The `-S` option is the suffix of the compressed file, the name determined in the last few lines.
- *Line 43:* empty the file by running `cat` on `/dev/null` and redirecting the output to the file. `/dev/null` is a special file on Linux systems which discards anything your write to it and returns `EOF` when read from. It is often used to discard output streams, but can also be used to empty a file, as shown here.

To test this script, you can create a logs directory and use `dd` to create some sample files over 10 megabytes in size:
```
$ dd if=/dev/zero of=logs/my-app.log  bs=1024  count=10240
10240+0 records in
10240+0 records out
10485760 bytes (10 MB, 10 MiB) copied, 0.0279485 s, 375 MB/s
$ touch logs/my-app.log.1.gz
$ dd if=/dev/zero of=logs/more-logs/my-app.log  bs=1024  count=10240
10240+0 records in
10240+0 records out
10485760 bytes (10 MB, 10 MiB) copied, 0.0415605 s, 252 MB/s
```
```
$ sudo ./rotate.sh logs/ .*/my-app.log
2022-09-18 20:38:36 UTC: compressing logs/my-app.log...
2022-09-18 20:38:36 UTC: compressing logs/more-logs/my-app.log...
$ ls logs/ logs/more-logs/
logs/:
more-logs  my-app.log  my-app.log.1.gz  my-app.log.2.gz

logs/more-logs/:
my-app.log  my-app.log.1.gz
```