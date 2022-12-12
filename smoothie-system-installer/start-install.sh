#!/bin/bash

WORK="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )" #$HOME/smoothie-processing-server

#this is the main installer program that do the install process for a smoothie processing server
echo "Installing Python Dependencies" &&
pip install simple-term-menu

echo "Beginning Install"
mkdir --parents $WORK/json
mkdir --parents $WORK/tmp

function refresh_timezones {
    rm -f $WORK/tmp/timezones.txt &&
    echo $(timedatectl list-timezones) >> $WORK/tmp/timezones.txt
    python $WORK/init/make_timezones_json.py
}
function refresh_keyboard_layouts {
    rm -f $WORK/tmp/keyboard_layouts.txt &&
    echo $(localectl list-keymaps) >> $WORK/tmp/keyboard_layouts.txt &&
    python $WORK/init/make_keyboard_layouts_json.py
}
function refresh_lsblk {
    rm -f $WORK/json/lsblk.json &&
    lsblk --json >> $WORK/json/lsblk.json
}

refresh_timezones &&
refresh_keyboard_layouts &&
refresh_lsblk &&

clear

python $WORK/server_select.py
