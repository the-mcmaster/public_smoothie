#!/bin/bash

#works only in the ran repo
WORK="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )" #smoothie arch iso repo directory

#syncs the required dependencies and fails otherwise
pacman -S archiso &&

#removes previous work
rm -f -r $WORK/work_dir/* &&
rm -f -r $WORK/out_dir/* &&
rm -f -r $WORK/releng_smoothie_custom/ &&

#copies the latest official arch iso image profile
cp -r /usr/share/archiso/configs/releng/ $WORK
mv $WORK/releng $WORK/releng_smoothie_custom

#the customization of the profile goes here
echo "git" >> $WORK/releng_smoothie_custom/packages.x86_64
echo "python-pip" >> $WORK/releng_smoothie_custom/packages.x86_64

#makes sure the program has the desired output file and sandbox directory
mkdir -p $WORK/work_dir
mkdir -p $WORK/out_dir

#the command to actually start making the new iso
mkarchiso -v -w $WORK/work_dir -o $WORK/out_dir $WORK/releng_smoothie_custom
