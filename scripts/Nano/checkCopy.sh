#!/bin/bash

#refresh file list
umount /media/l0r3zz/SCOUT
sleep 1
mount -o loop,rw,sync,dirsync,offset=210763776 /teslaflash/sdsusb.img /media/l0r3zz/SCOUT
sleep 2

cd /media/l0r3zz/SCOUT/TeslaCam/RecentClips
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

cd /tesladrive/l0r3zz/SCOUT/TeslaCam/SavedClips
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

cd /tesladrive/l0r3zz/SCOUT/TeslaCam/SentryClips
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

