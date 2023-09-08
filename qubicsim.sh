#!/bin/sh

# Function to launch qubic simulator

qubicsim 
{
	docker run -dp 9100:9100 nfruitwala/qubic-qce23-tutorial:latest&
	echo "Starting Docker image"
	sleep 30
	echo "Running Verilator build - takes about a minute"
	sleep 60
	echo "Building simulator - takes about 2 minutes"
	sleep 120
	echo "Simulator setup complete"
	echo "Starting Jupyter notebook"
	sleep 10
	jupyter notebook
}
