#! /bin/bash

# Execution note: our shell really must be bash or bash-compatible 
# This is because python's activiate script uses bash-isms.

sudo apt install --assume-yes python3-venv python3-pip
python3 -m venv venv && source venv/bin/activate

