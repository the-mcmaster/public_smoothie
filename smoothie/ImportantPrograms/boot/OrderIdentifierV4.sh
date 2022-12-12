#!/bin/bash

WORK="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && cd ../.. && pwd )"

OIcount="$(pgrep -c OrderIdentifier)"
cat /tmp/.smoothie-OrderIdentifierSelfLock-lock
SelfLockCode=$?

incre=0
#These if-then statements are testing for if an instance of this program is running and if so, is there a lock or not
#if the self lock doesn't exist and no other instance of this script is running
while [[ $incre -le 1 ]]
do
echo "[s:OrderIdentifier:$(date +"%D %T")] Starting Lock Test #"$(($incre+1)) "out of 2"
    if [ $SelfLockCode != "0" ] && [ $OIcount == "1" ];
    then
        #then make the self lock so no other instances of this script can start and then carry on

        echo "[s:OrderIdentifier:$(date +"%D %T")] Starting OrderIdentifier.sh"
        echo "[s:OrderIdentifier:$(date +"%D %T")] Self locked enabled"
        touch /tmp/.smoothie-OrderIdentifierSelfLock-lock


    #else if no self is found and there ARE multiple instances of this code running
    elif [ $SelfLockCode != "0" ] && [ $OIcount != "1" ];
    then
        echo "[s:OrderIdentifier:$(date +"%D %T")] Other instances of OrderIdentifier.sh found. Exiting..."
        echo "[s:OrderIdentifier:$(date +"%D %T")] Making a Self Lock for any further instances before exiting..."
        touch /tmp/.smoothie-OrderIdentifierSelfLock-lock
        exit 0


    elif [ $SelfLockCode == "0" ] && [ $OIcount != "1" ];
    then
        echo "[s:OrderIdentifier:$(date +"%D %T")] Other instances of OrderIdentifier.sh found. Exiting..."
        exit 0


    else
        echo "[s:OrderIdentifier:$(date +"%D %T")] Self lock already enabled"
        echo "[s:OrderIdentifier:$(date +"%D %T")] Starting program"


    fi

    echo "[s:OrderIdentifier:$(date +"%D %T")] Test #"$(($incre+1)) "Complete"
    ((incre+=1))
done

echo "[s:OrderIdentifier:$(date +"%D %T")] Beginning OrderIdentifier.sh"

running=0

while true
do

    echo "[s:OrderIdentifier:$(date +"%D %T")] Removing Downloader Lock"
    rm /tmp/.smoothie-OrderIdentifierOrderDownloadLock-lock

    #This while tests if a file exists in the temp folder
    while [ $running == 0 ]
    do
        echo "[s:OrderIdentifier:$(date +"%D %T")] Searching for a file"
        findtmp="$(find "$WORK/temp" -type f)"

        if [[ ! -z $findtmp ]]
        then
            echo "[s:OrderIdentifier:$(date +"%D %T")] file detected"
            ODCcount="$(pgrep -c ODCreator.sh)"

            if [[ $ODCcount == 0 ]]
            then
                running=1
            else


                while [[ "$ODCcount" != "0" ]]
                do
                    echo "[s:OrderIdentifier:$(date +"%D %T")] Instances of ODCreator.sh are running."
                    echo "[s:OrderIdentifier:$(date +"%D %T")] Waiting for these instances to finish."
                    sleep 1
                    ODCcount="$(pgrep -c ODCreator.sh)"
                    running=1
                done
            fi
        else
            echo "[s:OrderIdentifier:$(date +"%D %T")] nothing detected"
        fi

        sleep 1
    done

    #if /tmp/.smoothie-OrderDownloadOrderIdentifierLock-lock exists, then that means a batch of .zip files are being downloaded
    #therefore, this script must wait for this download to finish
    #once it is, OrderDownload.sh will remove the lock when it is done
    while [ -f /tmp/.smoothie-OrderDownloadOrderIdentifierLock-lock ]
    do
        echo "[s:OrderIdentifier:$(date +"%D %T")] A batch of files are currently being downloaded. Waiting for "
        sleep 10
    done

    #this lock will tell OrderDownloader.sh that it is NOT okay to start batches of downloads
    touch /tmp/.smoothie-OrderIdentifierOrderDownloadLock-lock
    echo "[s:OrderIdentifier:$(date +"%D %T")] Locking Ability for Incoming Orders to be Downloaded"
    echo "[s:OrderIdentifier:$(date +"%D %T")] Making Order Directories"


    #We have now ensured that there are absolutely no instances of ODCreator.sh running.
    #This fact alongside the fact that there can only be one instance of OrderIdentifier.sh running at a time,
    #means that it is not possible for more instances of ODCreator to be made until we make them in this instance of this script
    #Therefore, we can assume it is done processing the old batch of files
    #Any files in the temp folder now are simply the new batch
    #This also means that we can overwrite TopOrderFiles.txt without worry. (I would think about why that is. HINT: Its true, but why.)

    #As a premphasis for the next command, we will remove the old TopOrderFiles.txt file
    rm "$WORK/ImportantPrograms/PermanentKeys/TopOrderFiles.txt"
    #This variable goes into /temp and finds all the desired files
    find "$WORK/temp" -type f -name "OrderBlender-*.zip" | sed "s|.*/||" > "$WORK/ImportantPrograms/PermanentKeys/TopOrderFiles.txt"

    #to access any specific line of TopOrderFiles.txt, use the command "cat "$WORK/ImportantPrograms/PermanentKeys/TopOrderFiles.txt" | head -n ## | tail -1" where "##" is the specific line you wish to use
    #to know how many lines there are in TopOrderFiles.txt, use the command (wc -l < "$WORK/ImportantPrograms/PermanentKeys/TopOrderFiles.txt")



    i=0
    #THIS IS WHERE THE ORDERDIRECTORY BASH SCRIPT WILL GO NOW
    while [ $running == 1 ]
    do
        #The issue is now we have to start many instances of ODCreator.sh. This is so we can start doing processing as fast as possible for all orders.
        #Each instance of ODCreator.sh needs to access a unique ticket to begin processing



        #This program will first create a ticket (which will untimately be a number in a file somewhere) for the next instance of ODCreator.sh
        #Then it will create a lock.
        #Then it will start up an instance of ODCreator.sh
        #Then this script will wait for the lock to be removed.
        #   While this script waits for the locks to be removed, the instance of ODCreator.sh will look for it's ticket number.
        #   Once the instance of ODCreator.sh has retrived its number, it will never need to access that file again. Therefore, it removed the lock that was created by this script
        #   The removal of this lock will allow the logic of these comments to continue
        #We keep repeating this until we have begun processors to process each file


        #This program will first create a ticket (which will untimately be a number in a file somewhere) for the next instance of ODCreator.sh
        #lets code this
        #This is the ith time we have done this step
        i=$(($i+1))
        #Note: this means that for the logic of this while statement, when i=number of lines in TopOrderFiles.txt, then that is when we are done
        #We now grab the ith line of TopOrderFiles.txt. Hopefully, it is the name of the ith file we with to deal with.
        FileName="$(cat "$WORK/ImportantPrograms/PermanentKeys/TopOrderFiles.txt" | head -n $i | tail -1)"
        #Since FileName is suppossed to be in the form "OrderBlender-#.zip", we can get the order number, a.k.a the current ticket number, by removing "OrderBlender-" and ".zip" from the name
        TicketNumber="$( echo $FileName | sed 's/OrderBlender-//' | sed 's/.zip//' )"
        #For premphasis for the command after this one, we will remove the old "Ticket.txt"
        rm "$WORK/ImportantPrograms/PermanentKeys/Ticket.txt"
        #We will now put this number into an empty file called "Ticket.txt"
        echo "[s:OrderIdentifier:$(date +"%D %T")] $TicketNumber" > "$WORK/ImportantPrograms/PermanentKeys/Ticket.txt"
        #We have now created the ticket for our program

        #Then it will create a lock.
        #lets code this
        touch /tmp/.smoothie-OrderIdentifierODCreatorVariableLock-lock
        #We have now created the lock

        #Then it will start up an instance of ODCreator.sh
        #lets code this
        setsid "$WORK/ImportantPrograms/ODCreator.sh" &
        #We have now started up an instance of ODCreator.sh

        #Then this script will wait for the lock to be removed.
        #lets code this
        while [ -f /tmp/.smoothie-OrderIdentifierODCreatorVariableLock-lock ]
        do
            sleep 0.1
        done
        #the airplane is now off the runway and we are free to do as we wish and not care about the whatabouts of the instance of ODCreator.sh we just made
        #We have now forced this script to wait until the lock is removed. The instance of ODCreator that we just started will eventually remove it, so this while should be guarrentted to eventually end.

        #We keep repeating this until we have begun processors to process each file
        #lets code this
        #lets assume we are the ith order in /temp
        #then that means that we just got an instance of ODCreator.sh assined to us from the previous logic
        #then that means that there are no more files to process
        #therefore, if i is the number of the last file, and we are now done, then that means i is equal to the number of lines in TopOrderFiles.txt
        #therefore, end this while loop by making running=0 so we also get sent back to the standby loop where we look for files.
        if [ $i == "$(wc -l < "$WORK/ImportantPrograms/PermanentKeys/TopOrderFiles.txt")" ]
        then
            running=0
        fi

    done
done
