import sys
import cv2
import numpy as np
import traceback
import datetime
import darknet.python.dn3 as dn
import os
from os.path                            import splitext, basename
from glob                                       import glob
from darknet.python.dn3 import detect
from src.label                          import dknet_label_conversion
from src.utils import nms
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pytz

from pymongo import MongoClient
client = MongoClient()
db = client.sds_db
plate_detections=db.plateDetections

ocr_threshold = .4

ocr_weights = 'data/ocr/ocr-net.weights'.encode("utf-8")
ocr_netcfg  = 'data/ocr/ocr-net.cfg'.encode("utf-8")
ocr_dataset = 'data/ocr/ocr-net.data'.encode("utf-8")

ocr_net  = dn.load_net(ocr_netcfg, ocr_weights, 0)
ocr_meta = dn.load_meta(ocr_dataset)

class Watcher:
    DIRECTORY_TO_WATCH = "/tesladrive/detections/plates"

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            print("Received created event - %s." % event.src_path)
            try:
                    img_path = event.src_path

                    print('\tScanning %s' % img_path)

                    bname = basename(splitext(img_path)[0])

                    R, (width, height) = detect(ocr_net, ocr_meta, img_path, thresh=ocr_threshold, nms=None)

                    if len(R):

                            L = dknet_label_conversion(R, width, height)
                            L = nms(L, .45)

                            L.sort(key=lambda x: x.tl()[0])
                            lp_str = ''.join([chr(l.cl()) for l in L])

                            # change line below if you'd like a range (6 OR 7 character LPs, however false readings increase dramatically)
                            if 7 <= len(lp_str) <= 7:

                                    print('\t\tLP: %s' % lp_str)
                                    # get the timestamp based off of the frameImg filename
                                    file_name = os.path.basename(event.src_path).split('.')[0]
                                    video_date = file_name.split('_')[0]
                                    print(video_date)
                                    camera_location = file_name.split('-')[-2]
                                    print(camera_location)
                                    video_time = '-'.join(file_name.split('_')[1].split('-')[0:3])
                                    print(video_time)
                                    datetime_string = '{} {}'.format(video_date, video_time)
                                    print(datetime_string)
                                    video_start_time = datetime.datetime.strptime(datetime_string,
                                                                                  '%Y-%m-%d %H-%M-%S').timestamp()
                                    print(video_start_time)
                                    frame_time_seconds = (round(int(file_name.split('-')[-1].split('_')[0]) / 4) - 1)
                                    if frame_time_seconds > 0:
                                            frame_time_seconds = 0
                                    print(frame_time_seconds)
                                    tz = pytz.timezone('America/Los_Angeles')
                                    start_time_seconds = datetime.datetime.fromtimestamp(video_start_time, tz)
                                    print(start_time_seconds)
                                    print(int(start_time_seconds.strftime("%s")))
                                    detection_time = (int(start_time_seconds.strftime("%s")) + frame_time_seconds)
                                    print(detection_time)



                                    matching_poll = db.polls.find_one({"unixTS":detection_time})
                                    if matching_poll:
                                            print(matching_poll)
                                            existing_plate = db.plates.find_one({"plateContent": lp_str})
                                            if existing_plate:
                                                    post_data = {
                                                            'plateContent': lp_str,
                                                            'ts': detection_time,
                                                            'cameraLocation': camera_location,
                                                            'pollID': matching_poll['_id'],
                                                            'location': matching_poll['location'],
                                                            'driveID': matching_poll['driveID'] or undefined,
                                                            'speed': matching_poll['speed'],
                                                            'power': matching_poll['power'],
                                                            'heading': matching_poll['heading'],
                                                            'status': matching_poll['status'],
                                                            'detectionImgPath': event.src_path,
                                                            'plateID': existing_plate['_id'],
                                                            'vehicleImgPath': '/tesladrive/detections/vehicles/%s.png' % '_'.join(
                                                                    file_name.split('_')[:-1]),
                                                            'secondsIntoVideo': frame_time_seconds,
                                                            'videoFileName': '/tesladrive/backups/RecentClips/%s.mp4' % (
                                                                    '-'.join('_'.join(file_name.split('_')[:-2]).split(
                                                                            '-')[
                                                                             :-1]))
                                                    }

                                                    result = plate_detections.insert_one(post_data)
                                                    print('One plate detection added: {0}'.format(result.inserted_id))
                                            else:
                                                    new_plate = {
                                                            'plateContent': lp_str
                                                    }
                                                    plate_id = db.plates.insert_one(new_plate).inserted_id
                                                    post_data = {
                                                            'plateContent': lp_str,
                                                            'ts': detection_time,
                                                            'cameraLocation': camera_location,
                                                            'pollID': matching_poll['_id'],
                                                            'location': matching_poll['location'],
                                                            'driveID': matching_poll['driveID'] or undefined,
                                                            'speed': matching_poll['speed'],
                                                            'power': matching_poll['power'],
                                                            'heading': matching_poll['heading'],
                                                            'status': matching_poll['status'],
                                                            'detectionImgPath': event.src_path,
                                                            'plateID': plate_id,
                                                            'vehicleImgPath': '/tesladrive/detections/vehicles/%s.png' % '_'.join(
                                                                    file_name.split('_')[:-1]),
                                                            'secondsIntoVideo': frame_time_seconds,
                                                            'videoFileName': '/tesladrive/backups/RecentClips/%s.mp4' % (
                                                                    '-'.join('_'.join(file_name.split('_')[:-2]).split(
                                                                            '-')[
                                                                             :-1]))
                                                    }

                                                    result = plate_detections.insert_one(post_data)
                                                    print('One detection added: {0}'.format(result.inserted_id))
                                    else:
                                            print("no matching poll found")
                            else:
                                    print('plate detected too short, likely false positive: ', lp_str)
                    else:
                            print('No characters found')
            except:
                    traceback.print_exc()
                    sys.exit(1)

if __name__ == '__main__':
    w = Watcher()
    w.run()


