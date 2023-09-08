#!/bin/sh

# Function to connect to qubic hardware

CONPASS="Qubic2023"
DEST="user@baci-desktop.dhcp.lbl.gov"
echo"Creating a network tunnel to the hardware"
sshpass -p $CONPASS ssh -L 9090:localhost:9096 -N $DEST &
echo"Launching jupyter notebook"
jupyter notebook
