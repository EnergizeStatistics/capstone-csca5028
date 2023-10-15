#! /bin/bash
echo "python-$(python3 --version | awk '{print $2}')" > runtime.txt
