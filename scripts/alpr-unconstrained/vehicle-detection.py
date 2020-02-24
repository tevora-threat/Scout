import sys
import cv2
import numpy as np
import traceback

import darknet.python.darknet as dn

from src.label 				import Label, lwrite
from os.path 				import splitext, basename, isdir
from os 					import makedirs
from src.utils 				import crop_region, image_files_from_folder
from darknet.python.darknet import detect

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


vehicle_threshold = .5

vehicle_weights = b'/home/CHANGEME(USERNAME)/projects/alpr-unconstrained/data/vehicle-detector/yolo-voc.weights'
vehicle_netcfg = b'/home/CHANGEME(USERNAME)/projects/alpr-unconstrained/data/vehicle-detector/yolo-voc.cfg'
vehicle_dataset = b'/home/CHANGEME(USERNAME)/projects/alpr-unconstrained/data/vehicle-detector/voc.data'

vehicle_net = dn.load_net(vehicle_netcfg, vehicle_weights, 0)
vehicle_meta = dn.load_meta(vehicle_dataset)

output_dir = '/tesladrive/detections/vehicles'
output_dir_people = '/tesladrive/detections/people'


class Watcher:
	DIRECTORY_TO_WATCH = "/tesladrive/Frames"

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
				print('\tScanning %s' % event.src_path)
				try:
					img_path = event.src_path

					print('\tScanning %s' % img_path)

					bname = basename(splitext(img_path)[0])

					R, _ = detect(vehicle_net, vehicle_meta, img_path.encode('utf-8'), thresh=vehicle_threshold)
					P, _ = detect(vehicle_net, vehicle_meta, img_path.encode('utf-8'), thresh=vehicle_threshold)
					R = [r for r in R if r[0] in ['car', 'bus']]
					P = [p for p in P if p[0] in ['person']]

					print('\t\t%d cars found' % len(R))
					print('\t\t%d persons found' % len(P))

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

							cv2.imwrite('%s/%s_%dcar.png' % (output_dir, bname, i), Icar)

						# lwrite('%s/%s_cars.txt' % (output_dir, bname), Lcars)
					
					if len(P):

						Iorig = cv2.imread(img_path)
						WH = np.array(Iorig.shape[1::-1], dtype=float)
						Lpeople = []

						for i, r in enumerate(P):
							cx, cy, w, h = (np.array(r[2]) / np.concatenate((WH, WH))).tolist()
							print(cx,cy,w,h)
							tl = np.array([cx - w / 2., cy - h / 2.])
                        				tl = [tl[0]-.03,tl[1]-.03]
                        				if tl[0]<0:
                            					tl[0]=0.00
                        				if tl[1]<0:
                            					tl[1]=0.00
							br = np.array([cx + w / 2., cy + h / 2.])
							br = [br[0]+.03,br[1]+.03]
                        				if br[0]>1:
                            					br[0]=1.00
                        				if br[1]>1:
                            					br[1]=1.00
							label = Label(0, tl, br)
							Iperson = crop_region(Iorig, label)
                                                        print(tl,br)
							Lpeople.append(label)
							height,width,_ = Iperson.shape
                        				print(height,width)
							if width>320:
								cv2.imwrite('%s/%s_%dperson.png' % (output_dir_people, bname, i), Iperson)
							else:
								print('face likely too small to recognize')
								print('%s/%s_%dperson.png' % (output_dir_people, bname, i))

						# lwrite('%s/%s_cars.txt' % (output_dir, bname), Lcars)


				except:
					traceback.print_exc()
					sys.exit(1)


			except:
				traceback.print_exc()
				sys.exit(1)


		elif event.event_type == 'modified':
			# Taken any action here when a file is modified.
			print("Received modified event - %s." % event.src_path)


if __name__ == '__main__':
	w = Watcher()
	w.run()




