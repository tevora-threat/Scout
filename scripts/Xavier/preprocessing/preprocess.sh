#!/bin/bash

filename=$1
folderName=$(echo $filename|cut -d"." -f1)
echo "$folderName"
frameImgFileName=$(echo $folderName|cut -d/ -f5)
echo "$frameImgFileName"
ffmpeg -skip_frame nokey -i $filename -vsync 0 /tesladrive/Frames/$frameImgFileName-%d.png
echo "done"