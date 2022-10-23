Title: Implementing the GNU which utility in Python
Date: 2022-10-23
Author: Nathan Pezzotti
Category: python
Tags: python, programming
Image: which.jpg


This is an implentation of the `which` utility in Python, `which` can be run on Windows, MacOS, and Linux. The `which` utility prints the complete path to target executables on a system and can be useful for finding the install location of a program, or to check if a program is installed and in the path.

```python
#!/usr/bin/env python3

import os
import sys


def main(args):
    path = os.getenv('PATH')
    dirs = path.split(';') if sys.platform.startswith('win32') else path.split(':')

    results = { prog: [] for prog in args.program }
    for dir in dirs:
        with os.scandir(dir) as files:
            for file in files:
                if file.name in results and file.is_file():
                    results[file.name].append(file.path)

    exit_status = 0
    for _, files in results.items():
        if not files:
            exit_status = 1
            continue

        if args.a and not args.s:
            for f in files:
                print(f)
        elif not args.s:
            print(files[0])

    sys.exit(exit_status)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        description="Locate a program file in the user's path",
    )

    parser.add_argument(
        'program',
        nargs='+',
        help='List of command names'
    )
    parser.add_argument(
        '-a', 
        help="List all instances of executables found (instead of just the first one of each).", 
        action="store_true"
    )
    parser.add_argument(
        '-s', 
        help="No output, just return 0 if all of the executables are found, or 1 if some were not found.", 
        action="store_true"
    )

    args = parser.parse_args()

    main(args)
```

**Explanation of code:**

When the program is first run, the script checks to see if it is being executed directly and, if so, imports `argparse` module, which parses command line arguments. An `ArgumentParser` object is instantiated with the file name is the program name and a description. Arguments are then added to the instance using `add_argument`. The main arguments which need to be provided are (1. a list of programs, (2. the `-a` flag, which decides whether all instances of the executable will be printed or only the first in the path, and (3. the `-s` flag, which allows for nothing to be printed and only an exit code returned. The arguments passed to the script are parsed into a `argparse.Namespace` object with `parse_args` and saved as a variable named `args`, which is then passed to the `main` function.

The `main` function contains the logic to find the paths to the executables. It accepts an `argparse.Namespace` object which contains all the arguments provided to the script and will be used to determine the output. First, `os.getenv` is used to get the `PATH` variable (used on Windows, MacOS, and Linux) which is then split on either the semi-colon (Windows) or the colon (other platforms) using `sys.platform` to determine which it is executed on.

Next, a `results` dictionary is initialized using dict comprehension to set a key for each program passed as an argument with an empty list as its value. As each directory will need to be searched for the provided program, a `for` loop is declared to iterate over the paths parsed from the `PATH` variable.

For each directory, [`os.scandir`](https://docs.python.org/3/library/os.html#os.scandir) is used within a context manager to scan for matching files. It returns an iterator of `os.DirEntry` objects, representing all files in the directory. These objects containing useful file attributes, two of which are used in the next line. If the basename of the file is in the `results` dict and the file is a file, its absolute path is appended to the array for that file.

Once the directories have been scanned, the results will need to be printed depending on the flags provided to the program, and the program exit with a status code. `which` exits with `0` if executables were found and `1`, if not. To accomplish this, an `exit_status` variable is declared with an initial value `0`. Then, `results` is looped over to check if any paths exist for each file. If no matching files were found for a given program, `exit_status` is changed to `1` and the the iteration continues. If there are matching files, and `-a` was passed, the paths to the files are printed. If there are matching files and `-a` and `-s` were not passed, then the first path in the array is printed. If neither of the above clauses are true, then `-s` was passed and no files are printed. The program finally exits with the appropriate exit code, indicating whether or not each program passed to the script exists somewhere in the user's `PATH`.