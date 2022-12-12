#!/bin/bash

#this script will do all the initialization work for smoothie
#it will be the first script that starts up for smoothie
#it is not known currently what needs to be initialized, so this script will be made in modules that will run one after another
#modules will be made as they are needed in this script

WORK="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && cd ../.. && pwd )"

#Module 1: Creation and execution of pulse scripts in /tmp folder for VMs
numPotPul=$(ls $WORK/ImportantPrograms/VMInputShared | wc -l)

if [ $numPotPul == 0 ]
then

    echo "[s:Initialization.:$(date +"%D %T")] No virtual machine detected in $WORK/ImportantPrograms/VMInputShared..."
    echo "[s:Initialization.:$(date +"%D %T")] This is a fatal error..."
    echo "[s:Initialization.:$(date +"%D %T")] Exiting..."
    exit 1

else
    for i in $(seq 1 $numPotPul)
    do
        echo "[s:Initialization.:$(date +"%D %T")] Removing ready signal for VM$i as it is not ready..."
        rm $WORK/ImportantPrograms/VMInputShared/VM$i/ready
        echo "[s:Initialization.:$(date +"%D %T")] Creating pulseVM$i.sh for VM$i..."

        scriptL1="#!/bin/bash"
        scriptL2="i=$i"
        scriptL3="WORK=$WORK"
        echo $scriptL1 > /tmp/pulseVM$i.sh
        echo $scriptL2 >> /tmp/pulseVM$i.sh
        echo $scriptL3 >> /tmp/pulseVM$i.sh

        for j in $(seq 1 $(cat $WORK/ImportantPrograms/pulseSkeleton.txt | wc -l))
        do
            line=$(head -n $j $WORK/ImportantPrograms/pulseSkeleton.txt | tail -n 1)
            echo $line >> /tmp/pulseVM$i.sh
        done

        chmod +x /tmp/pulseVM$i.sh
        echo "[s:Initialization.:$(date +"%D %T")] Starting pulseVM$i.sh in /tmp..."
        setsid /tmp/pulseVM$i.sh &
    done
fi
