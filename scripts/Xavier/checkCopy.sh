#!/bin/bash

#refresh file list
umount /media/CHANGEME(USERNAME)/SCOUT #CHANGEME
sleep 1
mount -o loop,rw,sync,dirsync,offset=210763776 /teslaflash/sdsusb.img /media/CHANGEME(USERNAME)/SCOUT #CHANGEME
sleep 2

cd /media/CHANGEME(USERNAME)/SCOUT/TeslaCam/RecentClips #CHANGEME
for i in $(ls)
do
    if grep -Fxq $i /tesladrive/recentfiles.txt
    then
        #exists
        echo "$i exists, skipping"
    else
        #not found
        ffmpeg -err_detect ignore_err -i $i -c copy /tesladrive/Videos/$i && sync
        rm $i
	echo $i >> /tesladrive/recentfiles.txt
    fi
done

cd /tesladrive/CHANGEME(USERNAME)/SCOUT/TeslaCam/SavedClips #CHANGEME
for i in $(ls)
do
    if grep -Fxq $i /tesladrive/savedfolders.txt
    then
        #exists
        echo "$i exists, skipping"
    else
        #not found
        echo "$i not found"
        for video in $(ls $i)
        do
            ffmpeg -err_detect ignore_err -i $i/$video -c copy /tesladrive/Videos/$video && sync
            rm $i/$video
            #keeping the empty dir there for now to potentially later on write to mongo on whether the clip came from saved, sentry or recent
        done
        echo $i >> /tesladrive/savedfolders.txt
    fi
done

cd /tesladrive/CHANGEME(USERNAME)/SCOUT/TeslaCam/SentryClips #CHANGEME
for i in $(ls)
do
    if grep -Fxq $i /tesladrive/sentryfolders.txt
    then
        #exists
        echo "$i exists, skipping"
    else
        #not found
        echo "$i not found"
        for video in $(ls $i)
        do
            ffmpeg -err_detect ignore_err -i $i/$video -c copy /tesladrive/Videos/$video && sync
            rm $i/$video
            #keeping the empty dir there for now to potentially later on write to mongo on whether the clip came from saved, sentry or recent
        done
        echo $i >> /tesladrive/sentryfolders.txt
    fi
done
