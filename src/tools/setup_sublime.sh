#!/bin/bash
#
# PLEASE run this script by using:
# . setup_sublime.sh 
# Instead of ./setup_sublime.sh
# Because CWD issue can not allow you change directory!

# Constants
SUBLIME_HOME="$HOME"/Library/Application\ Support/Sublime\ Text\ 2


### Setup Git ###
cd "$SUBLIME_HOME"/Packages/
git clone git://github.com/kemayo/sublime-text-2-git.git Git


# Changing git_command path
cp "$SUBLIME_HOME"/Packages/Git/Git.sublime-settings  "$SUBLIME_HOME"/Packages/User/
perl -i -ple 's/,"git_command": false/,"git_command": "\/usr\/local\/git\/bin\/git"/g if $. == 7; close ARGV if eof' "$SUBLIME_HOME"/Packages/User/Git.sublime-settings


### Setup SublimeLinter ###
echo ""
cd "$SUBLIME_HOME"/Packages/
git clone https://github.com/SublimeLinter/SublimeLinter.git

echo ""
echo "Setup is completed. Enjoy~~~"
echo "You can use Command+Shift+p to call git comamnd set"
echo "You can also setup SublimeLinter by going to Perference->Package Settings->SublimeLinter" 