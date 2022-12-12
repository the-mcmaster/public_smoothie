#!/bin/bash

#This will be the download script for smoothie
#It will always be trying to download OrderBlender-#.zip files from the website and put it into the /temp directory
#If the file /tmp/.smoothie-OrderIdentifierOrderDownloadLock-lock exists, then do not download anything
#   wait until the lock goes away and then download it
#just before actively downloading, create the file /tmp/.smoothie-OrderDownloadOrderIdentifierLock-lock
#   this will stop OrderIdentifier from trying to process the files before they are fully downloaded
#   once finished downloading, remove /tmp/.smoothie-OrderDownloadOrderIdentifierLock-lock
#   this tell OrderIdentifier that it is all good to start processing everything in /temp

#for now, just remove the lock since there is no code here currently
#that way there is no way for this script to possibly stop OrderIdentifier
rm /tmp/.smoothie-OrderDownloadOrderIdentifierLock-lock
