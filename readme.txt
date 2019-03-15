## SPP Automation Scripts ##
This is a plugin repository for the RoboGalaxy automation framework. Installing RoboGalaxy is a requirement to use the scripts located in this repo.

## Installation ##

1.  Download and install the RoboGalaxy core libraries and utilities (https://ctf-pro.austin.hp.com/sf/projects/robogalaxy/)
2.  Install the prerequisites for this project using the command "python setup.py develop"

## Usage ##

1.	Switch branches (if necessary) with the command "git checkout <branch_name>" ("master" is used for all development work while "production" contains all production ready scripts)
2	All scripts are written in python and use the pybot launcher. The launcher command is:
		"pybot -v <variable_name1>:<variable_value1> -v <variable_name2>:<variable_value2> <script_name>.txt"
	Additional command usage and required variables can be found in the documentation section of each test suite file.


## Credits ##

CSI SPP Automation Team 
Mphasis - Bangalore