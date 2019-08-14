#!/bin/bash

#refresh file list
umount /media/CHANGEME(USERNAME)/SCOUT
sleep 1

#Offset below assumes you've set your partitions to the sizes used in README
mount -o loop,rw,sync,dirsync,offset=210763776 /teslaflash/sdsusb.img /media/CHANGEME(USERNAME)/SCOUT
sleep 2
cd /media/CHANGEME(USERNAME)/SCOUT/TeslaCam/RecentClips
for i in $(ls)
do
    if grep -Fxq $i /tesladrive/recentfiles.txt
    then
        #exists
        echo "$i exists, skipping"
    else
        #not found
        if [[ $i == *"front"* || $i == *"repeater"* ]]
        then
            mv $i /tesladrive/Videos/RecentClips/. && sync
            echo $i >> /tesladrive/recentfiles.txt
        fi
    fi
done

cd /media/CHANGEME(USERNAME)/SCOUT/TeslaCam/SavedClips
for i in $(ls)
do
    if grep -Fxq $i /tesladrive/savedfolders.txt
    then
        #exists
        echo "$i exists, skipping"
    else
        #not found
        #cp -R $i /tesladrive/Videos/SavedClips/.
        mv $i /tesladrive/Videos/SavedClips/. && sync
	echo $i >> /tesladrive/savedfolders.txt
    fi
done

