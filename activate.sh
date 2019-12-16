#!/bin/bash

if [ "$0" = "-bash" ]; then
    source env/dev/bin/activate
else
    echo "ERROR: run with source not sh"
    echo "usage: source setup.sh"
    exit
fi
