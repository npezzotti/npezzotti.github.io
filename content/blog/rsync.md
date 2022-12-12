Title: How to Use rsync Utility in Linux
Date: 2022-12-4
Author: Nathan Pezzotti
Category: linux
Tags: linux, networking
Image: terminal.jpg

`rsync` is a versatile and feature-rich copying utility which can be used for many purposes including copying data to and from a remote server and generating backups. `rsync` is known for its use of a delta-transfer algorithm, meaning it copies only those files which have changed between a given source and destination directory. This improves efficiency and reduces the overall amount of data processed locally or sent over the network.

The general syntax of `rsync` is as follows:
```bash
rsync [OPTIONS] <SOURCE> <DESTINATION>
```
In its most basic form, `rsync` can be used to copying a file to a destination within a given same server with a syntax similar to `cp`:
```bash
$ echo test > test.txt
$ rsync test.txt /tmp/   
$ cat /tmp/test.txt
test
```
To copy recursively, use the `-r` option.
```bash
$ mkdir test
$ touch test/file{0..10}
$ ls test
file0	file1	file10	file2	file3	file4	file5	file6	file7	file8	file9
$ rsync -r test /tmp      
$ ls /tmp
test
```
Important to note is that this copies the source directory `test` as a *subfolder* of the destination. To ignore the source directory and recursively copy only the files and subdirectories in the source directory to the destination directory, add a trailing slash.
```bash
$ rsync -r test/ /tmp
$ ls /tmp 
file0	file1	file10	file2	file3	file4	file5	file6	file7	file8	file9	test
```
To copy files from or to a remote server, you need to use a syntax similar to remote shell.
```bash
rsync [OPTIONS] <SOURCE> <USERNAME>@<REMOTE_HOST>:<DESTINATION>
```
The following `rsync` command copies a local file to the home directory on a remote server:

```bash
$ echo test > test.txt
$ rsync test.txt ubuntu@192.168.1.155:~
$ ssh ubuntu@192.168.1.155
ubuntu@ubuntu:~$ ls
ubuntu@ubuntu:~$ cat test.txt 
test
```
You can copy the file back by reversing the source and destination.
```bash
$ rsync ubuntu@192.168.1.155:~/test.txt test.copy.txt
$ ls
test.copy.txt	test.txt
```

## Notable options

Three options you often see used together with `rsync` are `-azv`. The `--archive` (`-a`) option is a shortcut to `-rlptgoD` and is commonly used as it copies recursively, copies symlinks, and preserves metadata on files, such as owner and modification times. Another common flag is `--verbose` (`-v`) which increases verbosity and prints information surrounding which files are being transferred and summary of the data transfer. `-z` compress the files, reducing the total amount of data transferred and improve speed.

When recursively copying, you may wish to specify which directories or files should be including in the operation. This can be done using the `--include` and `--exclude` flags along with a pattern matching the target files.

```
$ mkdir test
$ touch test/file{0..5}
$ rsync -azv --exclude '*0' test ubuntu@192.168.1.155:~
building file list ... done
test/
test/file1
test/file2
test/file3
test/file4
test/file5

sent 335 bytes  received 136 bytes  62.80 bytes/sec
total size is 0  speedup is 0.00
```
`--dry-run` will run through all actions to be taken, without actually performing those actions. This is useful for understanding what files will be copied given the command structure, for example:
```bash
$ rsync -av --dry-run test/file[1-2] ubuntu@192.168.1.155:~/
building file list ... done
file1
file2

sent 106 bytes  received 32 bytes  9.52 bytes/sec
total size is 0  speedup is 0.00
```

Rsync connects to remote servers using SSH by default and can support specific SSH options with the `--rsh` (`-e`) flag. The `--rsh` flag allows you to customize the remote shell command with additional options, or use a different remote shell program altogether. For example, here is how to specify the port the remote server's `sshd` daemon is listening on.
```bash
rsync -e 'ssh -p 22200' test/ ubuntu@192.168.1.155:~/
```

As file transfers can take time to complete, using the `--progress` flag will show the data transfer progress for each file:
```bash
rsync -rzv --progress test ubuntu@192.168.1.155:~
building file list ... 
12 files to consider
test/
test/file0
           0 100%    0.00kB/s    0:00:00 (xfer#1, to-check=10/12)
test/file1
           0 100%    0.00kB/s    0:00:00 (xfer#2, to-check=9/12)
test/file10
           0 100%    0.00kB/s    0:00:00 (xfer#3, to-check=8/12)
test/file2
           0 100%    0.00kB/s    0:00:00 (xfer#4, to-check=7/12)
test/file3
           0 100%    0.00kB/s    0:00:00 (xfer#5, to-check=6/12)
test/file4
           0 100%    0.00kB/s    0:00:00 (xfer#6, to-check=5/12)
test/file5
           0 100%    0.00kB/s    0:00:00 (xfer#7, to-check=4/12)
test/file6
           0 100%    0.00kB/s    0:00:00 (xfer#8, to-check=3/12)
test/file7
           0 100%    0.00kB/s    0:00:00 (xfer#9, to-check=2/12)
test/file8
           0 100%    0.00kB/s    0:00:00 (xfer#10, to-check=1/12)
test/file9
           0 100%    0.00kB/s    0:00:00 (xfer#11, to-check=0/12)

sent 572 bytes  received 268 bytes  152.73 bytes/sec
total size is 0  speedup is 0.00
```
For cases where you want to delete the source files after a succesful transfer, you can use the `--remove-source-files`.
```bash
$ rsync -rv --remove-source-files test/ ubuntu@192.168.1.155:~
building file list ... done
file0
file1
file10
file2
file3
file4
file5
file6
file7
file8
file9

sent 594 bytes  received 262 bytes  131.69 bytes/sec
total size is 0  speedup is 0.00
$ ls test/
$ 
```

As mentioned at the start of this post, of the most important distinctions of the `rsync` utility is which can be seen in the following example. Notice in the second transfer that only `file6` is sent over the network.

```
$ mkdir test
$ touch test/file{0..5}
$ rsync -azv test ubuntu@192.168.1.188:~ 
building file list ... done
test/
test/file0
test/file1
test/file2
test/file3
test/file4
test/file5

sent 382 bytes  received 158 bytes  83.08 bytes/sec
total size is 0  speedup is 0.00
$ touch test/file6
$ rsync -azv test ubuntu@192.168.1.188:~
building file list ... done
test/
test/file6

sent 203 bytes  received 48 bytes  45.64 bytes/sec
total size is 0  speedup is 0.00
$ 
```

As shown above, the `rsync` utility is a powerful tool for Linux users and can serve many purposes related to data transfer. This guide has shown some core workflows as a starting point, though are many additional options and functions which can be explored further by consulting the `rsync` `man` page.