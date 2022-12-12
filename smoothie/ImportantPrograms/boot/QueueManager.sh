#!/bin/bash

#this program will look for tickets made by ODCreator.sh as a signal that the file is ready for a VM
#When a VM gives the signal to Queue manager that it is ready for a folder heirarchy, Queue manager will look at the Queue list
#and pick the heirarchy with the lowest order number (as in it is the oldest order needing to be processed since order numbers are made by date)

#this program is essentially the input bridge between host machine and virtual machine

#Some future additions to this program may be
#   -to allow users to specify how much processing they wish to use, the queue manager will organize order by GPU

WORK="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && cd ../.. && pwd )"

OIcount="$(pgrep -c QueueManager.sh)"
cat /tmp/.smoothie-QueueManagerSelfLock-lock
SelfLockCode=$?

incre=0
#These if-then statements are testing for if an instance of this program is running and if so, is there a lock or not
#if the self lock doesn't exist and no other instance of this script is running
while [[ $incre -le 1 ]]
do
echo "[s:QueueManager.sh:$(date +"%D %T")] Starting Lock Test #"$(($incre+1)) "out of 2"
    if [ $SelfLockCode != "0" ] && [ $OIcount == "1" ];
    then
        #then make the self lock so no other instances of this script can start and then carry on

        echo "[s:QueueManager.sh:$(date +"%D %T")] Starting QueueManager.sh"
        echo "[s:QueueManager.sh:$(date +"%D %T")] Self locked enabled"
        touch /tmp/.smoothie-QueueManagerSelfLock-lock


    #else if no self is found and there ARE multiple instances of this code running
    elif [ $SelfLockCode != "0" ] && [ $OIcount != "1" ];
    then
        echo "[s:QueueManager.sh:$(date +"%D %T")] Other instances of QueueManager.sh found. Exiting..."
        echo "[s:QueueManager.sh:$(date +"%D %T")] Making a Self Lock for any further instances before exiting..."
        touch /tmp/.smoothie-QueueManagerSelfLock-lock
        exit 0


    elif [ $SelfLockCode == "0" ] && [ $OIcount != "1" ];
    then
        echo "[s:QueueManager.sh:$(date +"%D %T")] Other instances of QueueManager.sh found. Exiting..."
        exit 0


    else
        echo "[s:QueueManager.sh:$(date +"%D %T")] Self lock already enabled"
        echo "[s:QueueManager.sh:$(date +"%D %T")] Starting program"


    fi

    echo "[s:QueueManager.sh:$(date +"%D %T")] Test #"$(($incre+1)) "Complete"
    ((incre+=1))
done




echo "[s:QueueManager.sh:$(date +"%D %T")] Beginning QueueManager.sh"




#we want this to never stop running, so this will always run under a forever loop
while true
do
    sleep 1
    echo "[s:QueueManager.sh:$(date +"%D %T")] Starting New Check"

    #we check to see if there are any orders needing to be processed
    while [ -z "$(ls -A $WORK/ImportantPrograms/InQueue)" ]; do
        echo "[s:QueueManager.sh:$(date +"%D %T")] No files ready in queue!"
        echo "[s:QueueManager.sh:$(date +"%D %T")] resting for 5 seconds..."
        sleep 5
    done

    echo "[s:QueueManager.sh:$(date +"%D %T")] File Detected!"
    echo "[s:QueueManager.sh:$(date +"%D %T")] Checking for any ready-to-render Virtual Machine!"

    #we need to check if any VMs are done
    #   if so, we need to give the ready VM(s) any awaiting order(s)
    #       before we send a file to a VM, check that the virtual machine is in a state where it can accept a file
    #   if not, then we sleep for 5 seconds and try again

    #   if not, then we sleep for 5 seconds and try again
    while [ -z "$(ls -A $WORK/ImportantPrograms/VMReadyKeys)" ]
    do
        echo "[s:QueueManager.sh:$(date +"%D %T")] No Virtual Machines ready for new rendering orders..."
        sleep 5
    done

    #if we exit the loop above, then this means that a virtual machine is ready to go
    echo "[s:QueueManager.sh:$(date +"%D %T")] Open Virtual Machine slot detected!"
    echo "[s:QueueManager.sh:$(date +"%D %T")] Beginning process to fill Virtual Machine slot..."

    #   if so, we need to give the ready VM(s) any awaiting order(s)
    #we have to now find the ticket with the smallest order number
    #   this will be the order that we will give to a ready virtual machine
    OrderNumber=$(ls -v $WORK/ImportantPrograms/InQueue/ | head -n 1 | rev | cut -c7- | rev)
    echo "[s:QueueManager.sh:$(date +"%D %T")] Processing order number ""$OrderNumber"

    #we must find A virtual machine for our order
    #here, we look in the VMReadyKeys dir
    VirtualMachine=$(ls $WORK/ImportantPrograms/VMReadyKeys | head -n 1)

done
