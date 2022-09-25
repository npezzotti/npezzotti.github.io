Title: Bash Script to View and Save Shell Prompts
Date: 2022-09-25
Author: Nathan Pezzotti
Category: linux
Tags: linux, programming
Image: prompts.jpg

Below is a bash script I worked on which allows users to save shell prompts as profiles for reuse. If run without arguments, the script will prompt you to select one of your saved prompts and print commands to apply it to either the current shell session or to all future sessions. To save a prompt, you can run the script with the optional `prompt` argument, which is a single-quoted prompt you want to save for re-use. 

An interesting feature of this script is its use of prompt expansion, which was introduced in Bash 4.4. Prompt expansion allows you to view the expanded prompt in the output without having to modify `PS1`. 

```shell
#!/usr/bin/env bash

set -e

PROGRAM_NAME="$(basename ${0})"
PROMPT="$1"
PROMPTS_FILE="/home/${USER}/.prompts"

help()
{
   echo ""
   echo "${PROGRAM_NAME}: $PROGRAM_NAME [prompt]"
   echo "	Save bash prompts for reuse. Prompts are saved to ${PROMPTS_FILE}."
   echo ""
   echo " 	Options:"
   echo "	  prompt	A bash prompt to save (must be double quoted)"
   echo "	  -h		Print this help"
   echo ""
}

for ARG in "$@"
do
    case $ARG in
		-h|-H)	help
			exit
			;;
		*)	continue
			;;
	esac
done

if [ -n "$PROMPT" ]
then
	echo "Expanded prompt: ${PROMPT@P}"
	read -n 2 -p "Save this prompt? (y/n)? "

	case "$REPLY" in
        y|Y)
			read -p "Enter prompt name: " PROMPT_NAME
			if [ "$(grep -e ^${PROMPT_NAME}$'\t' $PROMPTS_FILE | awk -F '\t' '{print $1}')" = "$PROMPT_NAME" ]
			then
				echo "Prompt with name "$PROMPT_NAME" already exists."
				exit 1
			fi
			echo -ne "${PROMPT_NAME}\t" >> $PROMPTS_FILE
			echo "$PROMPT" >> $PROMPTS_FILE
			echo "Saved \"${PROMPT_NAME}\"."
			exit 0
			;;
		*)	
			echo "Prompt not saved."
			exit 1
			;;
	esac
else
	if [ -f "$PROMPTS_FILE" ]
	then
		LINE_NO=1
		while IFS=$'\t' read -r name prompt
		do
			echo "${LINE_NO}). $name: ${prompt@P}"
			((LINE_NO++))
		done < "$PROMPTS_FILE"
		echo ""
		read -n 4 -p "Select prompt: " SELECTED_PROMPT
		if [[ "$SELECTED_PROMPT" =~ ^[[:digit:]]{1,3}$ ]]
		then
			PROMPT=$(sed "${SELECTED_PROMPT}q;d" $PROMPTS_FILE | awk -F '\t' '{print $2}')
			cat <<-EOF
				
				Run this command to apply prompt to current session:
					export PS1="${PROMPT}"

				Or, make the change permanent by modifying your .bashrc:
					echo 'export PS1="${PROMPT}"' >> /home/${USER}/.bashrc

			EOF
		else
			echo "Invalid entry."
			exit 1
		fi
	else
		echo "No prompts to display."
		exit 1
	fi
fi
```
### Explanation of code:

- *Line 1:* this is a shebang, which tells the kernel what program to use to execute the script. In this, I use `/usr/bin/env bash` which has the benefit of finding the path to `bash` using the current shell environment. Running `env` alone prints all environment variables present on the system, including `$PATH` which, in this case, will be used to locate the interpreter (`bash`), improving portability.
- *Line 3:* `set` is a shell builtin which is used to change shell options. Running it with the `-e` flag changes the shell settings so that the script exits if any command exits with an error.
- *Lines 5-7:* here I'm declaring some variables to be used later. `PROGRAME_NAME` is the name of the script- `$0` returns the relative path to the script, which I use the `basename` command on to extract only the file name. `PROMPT` is the optional prompt to be saved and set to the value of the first argument passed to the script (`$1`). `PROMPTS_FILE` is the file where prompts are saved- the path to the user's home directory is dynamically generated using the `$USER` envionment variable, which returns the user's username.
- *Lines 9-19:* this is a bash function which prints the usage menu to the screen. 
- *Lines 21-30:* here I am using a bash for loop to loop through`$@`, which expands to all positional arguments provided the script. Within this loop, there is a switch statement to see if any of the arguments are `-h` or `-H`, in which case the script prints the help menu and exits. If the argument is anything else, the switch statement continues looping through the arguments.
- *Lines 32-87:* this is a large bash `if` statement which determines the use of the script as being either for saving a prompt, or retrieving one.

**Path one: a prompt was provided**

- *Lines 32-33:* here, the script tests to see that `PROMPT` is a string with a length greater than zero, which is true if the user passes an argument to the script.
- *Lines 34-35:* here, the value passed to the script is display using prompt expansion (`@P`), allowing the user to see what the prompt will look like before making any changes. Then, the user is prompted to save the prompt with the `read` command. `read` provides a prompt (`-p`) and accepts user input, which I restrict to 2 characters with `-n` (any character and a carriage return).
- *Lines 37-55:* this is a switch statement to validate the user input. It tests the value of `REPLY` which is the default variable returned by the read command with the user input.
    - *Lines 38-44:* if the user inputs `y` or `Y`, the `read` command is run to accept a name for the prompt (which will be savd in `PROMPT_NAME`). Then, a bash `if` statement checks to see if the value input already exists. To do so, a condition is provided using command expansion, to see if the returned string is equal to the provided prompt. 
        - `"grep -e ^${PROMPT_NAME:=""}$'\t' $PROMPTS_FILE` searches the user's `.prompts` file to see if a prompt with `PROMPT_NAME` already exists. `grep` is run with the `-e` option to match a regex, the regex here asserting that the prompt name be at the beginning of the line and preceded by a tab character.
        - Matching lines are then piped into `awk -F '\t' '{print $1}'`, which breaks the line on the tab character, specified with the `-F` option, and returns only the first part (the name of the prompt). This is finally compared to the input prompt name using the `=` operator to see if they are the same and, if so, the script exits.
    - *Lines 45-49:* if the prompt doesn't exist, the new prompt is saved to the user's `.prompts` file. This is done in multiple echo statements as, in order to add a tab character, `echo` needs to be run with the `-e` flag in order to interprate backslash escapes. If the prompt is printed to the file with the `-e` flag however, it will have the unwanted effect of modifying the characters. Therefore, the first `echo` statement adds the name of the prompt followed by an interpretated tab character (`-e`) and no newline (`-n`), to which the second `echo` statement can append the prompt.
    - *Lines 50-52:* if the user entered anything but case-insensitive `y`, exit.

**Path two: a prompt was not provided**

- *Line 55:* test to see if the user's `.prompts` file exists on the system, using the `-f` test. If it does not, the script exists as their are no prompts saved.
- *Lines 56-62:* this a a bash `while` loop which reads in all lines of the user's `.prompts` file and displays them to the screen. A `LINE_NO` variable is declared in order to keep track of the line number in the file. The `read` command is run with a modification `IFS`, which `read` uses as a delimiter (usually a space). Since the separator between the prompt name and the prompt is a tab, that is used for the value of `IFS` to yield a name and value per line. Then, the line number, prompt name, and expanded prompt are displayed to the screen.
- *Line 63:* prompt the user for which number prompt they want to use and save it as `SELECTED_PROMPT`
- *Line 64:* this `if` statement tests the value of `SELECTED_PROMPT` using `[[]]`, which supports the `=~` operator to check that the value matches a regex. The regex requires the user enter a number between 1-3 characters in length. If this fails, the script exits.
- *Lines 66-75:* search the user's `.prompts` file to return only the line containing the selected prompt. To do this, `sed` is used with the `d` command. The file is read in by sed and each line discarded until `SELECTED_PROMPT` is reached, at which point `sed` exits, returning that line. This is piped into `awk`, which uses the tab character as a delimiter to retrieve the name and prompt and return only the prompt (`$2`). Finally, the prompt is formatted to provide the user with two commands to either modify `PS1` in the current session, or make a more permanent change to the `.bashrc`. This output is printed by cat using a heredoc with the `<<-` redirection operator, to ensure it ignores the tab all leading tab characters in the text.