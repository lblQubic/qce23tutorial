#!/bin/sh
# Progress bar code is from Teddy Skarin 
#(https://github.com/fearside/ProgressBar.git)
# Function to launch qubic simulator

function qubicsim 
{
	docker run -dp 9100:9100 nfruitwala/qubic-qce23-tutorial:latest&
#	echo "Starting Docker image"
#	sleep 30
#	echo "Running Verilator build - takes about a minute"
#	sleep 60
#	echo "Building simulator - takes about 2 minutes"
#	sleep 120
#	echo "Simulator setup complete"
#	echo "Starting Jupyter notebook"
#	sleep 10
}

function ProgressBar {
# Process data
	let _progress=(${1}*100/${2}*100)/100
	let _done=(${_progress}*4)/10
	let _left=40-$_done
# Build progressbar string lengths
	_done=$(printf "%${_done}s")
	_left=$(printf "%${_left}s")

# 1.2 Build progressbar strings and print the ProgressBar line
# 1.2.1 Output example:
# 1.2.1.1 Progress : [########################################] 100%
printf "\rQubiC Simulator Progress : [${_done// /#}${_left// /-}] ${_progress}%%"

}

# Variables
_start=1

# This accounts as the "totalState" variable for the ProgressBar function
_end=100

echo "Simulator setup takes about 3 minutes"
qubicsim
sleep 5
for number in $(seq ${_start} ${_end})
do
	ProgressBar ${number} ${_end}
	sleep 2
done
echo "Starting Jupyter notebook"
jupyter notebook
