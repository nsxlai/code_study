#!/bin/bash
clear

# make sure to install the following package first
# sudo apt install sysbench
# sudo apt install hdparm

for f in {1..7}
do
    vcgencmd measure_temp
    sysbench --test=cpu --cpu-max-prime=25000 --num-threads=4 run > /dev/null
    sudo hdparm -t --direct /dev/sda
done

vcgencmd measure_temp