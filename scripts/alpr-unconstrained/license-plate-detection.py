import sys
import cv2
import numpy as np
import traceback

import darknet.python.darknet as dn

from src.label import Label, lwrite
from os.path import splitext, basename, isdir
from os import makedirs
from src.utils import crop_region, image_files_from_folder
from darknet.python.darknet import detect

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

lp_threshold = .5

vehicle_weights = 'data/lp2/darknet-yolov3_final.weights'.encode("utf-8")
vehicle_netcfg = 'data/lp2/darknet-yolov3.cfg'.encode("utf-8")
vehicle_dataset = 'data/lp2/darknet.data'.encode("utf-8")

vehicle_net = dn.load_net(vehicle_netcfg, vehicle_weights, 0)
vehicle_meta = dn.load_meta(vehicle_dataset)
output_dir='/tesladrive/detections/plates'


class Watcher:
    DIRECTORY_TO_WATCH = "/tesladrive/detections/vehicles"

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
                img_path=event.src_path
                print('\tScanning %s' % img_path)

                bname = basename(splitext(img_path)[0])

                R, _ = detect(vehicle_net, vehicle_meta, img_path, thresh=lp_threshold)

                R = [r for r in R if r[0] in ['vehicle registration plate']]

                print('\t\t%d plates found' % len(R))

                if len(R):

                    Iorig = cv2.imread(img_path)
                    WH = np.array(Iorig.shape[1::-1], dtype=float)
                    Lcars = []

                    for i, r in enumerate(R):
                        cx, cy, w, h = (np.array(r[2]) / np.concatenate((WH, WH))).tolist()
                        tl = np.array([cx - w / 2., cy - h / 2.])
                        br = np.array([cx + w / 2., cy + h / 2.])
                        label = Label(0, tl, br)
                        Icar = crop_region(Iorig, label)


                        Lcars.append(label)
                        height,width,_ = Icar.shape
                        print(height,width)
                        if height>24:
                            cv2.imwrite('%s/%s_%dplate.png' % (output_dir, bname, i), Icar)
                        else:
                            print('plate likely too small to OCR, high change of FP')
                    
            except:
                traceback.print_exc()
                sys.exit(1)


        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            print("Received modified event - %s." % event.src_path)


if __name__ == '__main__':
    w = Watcher()
    w.run()


