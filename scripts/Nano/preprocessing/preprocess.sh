#!/bin/bash

filename=$1
echo "filename is $filename"
videoDate=$(echo $filename|cut -d"_" -f1)
echo "Date of video was $videoDate"
videoTime=$(echo $filename|cut -d"_" -f2|cut -d"-" -f1-3|tr - :)
echo "Start time of video was $videoTime"
camera=$(echo $filename|cut -d"." -f1|rev|cut -d"-" -f1|rev)
echo "Camera used for detection was $camera"
folderName=$(echo $filename|cut -d"." -f1)
echo "$folderName"

frameImgFileName=$(echo $folderName|cut -d/ -f4)

echo "$frameImgFileName"
ffmpeg -skip_frame nokey -i $filename -vsync 0 /tesladrive/Frames/$frameImgFileName-%d.png
echo "done"
