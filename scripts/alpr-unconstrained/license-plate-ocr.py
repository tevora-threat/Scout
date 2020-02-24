import sys
import cv2
import numpy as np
import traceback
import datetime
import darknet.python.dn3 as dn
import os
from os import path
from os.path import splitext, basename
from glob import glob
from darknet.python.dn3 import detect
from src.label import dknet_label_conversion
from src.utils import nms
import time
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pytz
from bson.objectid import ObjectId
from pymongo import MongoClient

client = MongoClient('CHANGEME')
db = client.sds_db

plate_detections = db.plateDetections

# after first run:
# homestate=db.user_settings.find_one({"stateSet":true})['homestate']

# first run:
user_settings = db.userSettings

homestate = db.user_settings.find_one({"stateSet": True})
if homestate:
    homestate = homestate['homestate']
else:
    state_post_data = {'stateSet': True, 'homestate': 'CA'}
    user_settings.insert_one(state_post_data)
    homestate = 'CA'

ocr_threshold = .4

ocr_weights = '/home/CHANGEME(USERNAME)/projects/alpr-unconstrained/data/ocr/ocr-net.weights'.encode("utf-8")
ocr_netcfg = '/home/CHANGEME(USERNAME)/projects/alpr-unconstrained/data/ocr/ocr-net.cfg'.encode("utf-8")
ocr_dataset = '/home/CHANGEME(USERNAME)/projects/alpr-unconstrained/data/ocr/ocr-net.data'.encode("utf-8")

ocr_net = dn.load_net(ocr_netcfg, ocr_weights, 0)
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

                    # with open('%s/%s_str.txt' % (output_dir, bname), 'w') as f:
                    #         f.write(lp_str + '\n')
                    # change line below if you'd like a range (6 OR 7 character LPs, however false readings increase dramatically)
                    if 7 <= len(lp_str) <= 7:

                        print('\t\tLP: %s' % lp_str)
                        # get the timestamp based off of the frameImg filename
                        file_name = os.path.basename(event.src_path).split('.')[0]
                        video_date = file_name.split('_')[0]
                        print(video_date)
                        camera_location = file_name.split('-')[-2]
                        print(camera_location)
                        # pre_video_time = file_name.split('_')[1]
                        video_time = '-'.join(file_name.split('_')[1].split('-')[0:3])
                        print(video_time)
                        datetime_string = '{} {}'.format(video_date, video_time)
                        print(datetime_string)
                        video_start_time = datetime.datetime.strptime(datetime_string,
                                                                      '%Y-%m-%d %H-%M-%S').timestamp()
                        print(video_start_time)
                        frame_time_seconds = (round(int(file_name.split('-')[-1].split('_')[0]) / 4) - 1)
                        if frame_time_seconds < 0:
                            frame_time_seconds = 0
                        print(frame_time_seconds)
                        tz = pytz.timezone('America/Los_Angeles')
                        start_time_seconds = datetime.datetime.fromtimestamp(video_start_time, tz)
                        print(start_time_seconds)
                        print(int(start_time_seconds.strftime("%s")))
                        detection_time = (int(start_time_seconds.strftime("%s")) + frame_time_seconds)
                        print(detection_time)

                        matching_poll = db.polls.find_one({"unixTS": detection_time})
                        if matching_poll:
                            print(matching_poll)

                            # does the poll have a geocodeID?
                            ####geocode temp fix, for testing. everything in prod will have a street value
                            reqHeaders = {'User-Agent': 'SDScout/0.0.1'}
                            reqGeoCode = requests.get(
                                url='https://nominatim.openstreetmap.org/reverse?format=json&lat={}&lon={}&zoom=18&addressdetails=1'.format(
                                    matching_poll['location']['coordinates'][1],
                                    matching_poll['location']['coordinates'][0]), headers=reqHeaders)
                            print(reqGeoCode.json())
                            geoObject = reqGeoCode.json()
                            # reqGeoCode.json()[0]['year']

                            # now save geocode as it's own document for forward compatibility
                            new_geocode = {
                                'place_id': geoObject['place_id'],
                                'osm_type': geoObject['osm_type'],
                                'osm_id': geoObject['osm_id'],
                                'location': {
                                    'type': "Point",
                                    'coordinates': [geoObject['lon'], geoObject['lat']]
                                },
                                'display_name': geoObject['display_name'],
                                'road': geoObject['address']['road'],
                                'city': geoObject['address']['city'],
                                'county': geoObject['address']['county'],
                                'state': geoObject['address']['state'],
                                'postcode': geoObject['address']['postcode'],
                                'country': geoObject['address']['country'],
                                'country_code': geoObject['address']['country_code'],
                                'boundingbox': geoObject['boundingbox']
                            }
                            geocode_id = db.geocodes.insert_one(new_geocode).inserted_id

                            # update the matching poll doc
                            db.Doc.update({"_id": matching_poll["_id"]},
                                          {"$set": {'street': geoObject['address']['road'],
                                                    'city': geoObject['address']['city'],
                                                    'geocodeID': geocode_id, }})
                            ####end temp geocode fix

                            existing_plate = db.plates.find_one({"plateContent": lp_str})

                            if existing_plate:
                                print('plate exists!', existing_plate)
                                post_data = {
                                    'plateContent': lp_str,
                                    'ts': detection_time,
                                    'cameraLocation': camera_location,
                                    'pollID': matching_poll['_id'],
                                    'location': matching_poll['location'],
                                    'driveID': matching_poll['driveID'] or undefined,
                                    'speed': matching_poll['speed'],
                                    'street': geoObject['address']['road'],
                                    'city': geoObject['address']['city'],
                                    'geocodeID': geocode_id,
                                    'power': matching_poll['power'],
                                    'heading': matching_poll['heading'],
                                    'status': matching_poll['status'],
                                    'detectionImgPath': event.src_path,
                                    'plateID': existing_plate['_id'],
                                    'vyear': existing_plate['vyear'],
                                    'vmake': existing_plate['vmake'],
                                    'vmodel': existing_plate['vmodel'],
                                    'vehicleImgPath': '/tesladrive/detections/vehicles/%s.png' % '_'.join(
                                        file_name.split('_')[:-1]),
                                    'secondsIntoVideo': frame_time_seconds,
                                    'videoFileName': '/tesladrive/Videos/%s.mp4' % (
                                        '-'.join('_'.join(file_name.split('_')[:-2]).split(
                                            '-')[
                                                 :-1]))
                                }

                                result = plate_detections.insert_one(post_data)
                                print('One plate detection added: {0}'.format(result.inserted_id))

                            else:
                                # we need to create a doc in PLATES first, get that objectID, then add the plateDetection

                                # but first we need to do the make model lookup
                                session = requests.Session()
                                session.headers.update({
                                                           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:69.0) Gecko/20100101 Firefox/69.0'})
                                reqMakeModel = session.get(
                                    'https://www.carfax.com/api/mobile-homepage-quickvin-check?plate={}&state={}'.format(
                                        lp_str, homestate))


                                newVyear = '-'
                                newVmake = '-'
                                newVmodel = '-'
                                print(reqMakeModel.json())

                                try:
                                    newVyear = reqMakeModel.json()['quickVinResults'][0]['year']
                                    newVmake = reqMakeModel.json()['quickVinResults'][0]['make']
                                    newVmodel = reqMakeModel.json()['quickVinResults'][0]['model']
                                except:
                                    print('plate not found')

                                new_plate = {
                                    'plateContent': lp_str,
                                    'vyear': newVyear,
                                    'vmake': newVmake,
                                    'vmodel': newVmodel
                                }
                                plate_id = db.plates.insert_one(new_plate).inserted_id

                                # dont forget to add geocode

                                ####geocode temp fix, for testing. everything in prod will have a street value
                                # this is a parked detection so we need to get geocode
                                reqHeaders = {'User-Agent': 'SDScout/0.0.1'}
                                reqGeoCode = requests.get(
                                    url='https://nominatim.openstreetmap.org/reverse?format=json&lat={}&lon={}&zoom=18&addressdetails=1'.format(
                                        matching_poll['location']['coordinates'][1],
                                        matching_poll['location']['coordinates'][0]), headers=reqHeaders)
                                print(reqGeoCode.json())
                                geoObject = reqGeoCode.json()
                                # reqGeoCode.json()[0]['year']

                                # now save geocode as it's own document for forward compatibility
                                new_geocode = {
                                    'place_id': geoObject['place_id'],
                                    'osm_type': geoObject['osm_type'],
                                    'osm_id': geoObject['osm_id'],
                                    'location': {
                                        'type': "Point",
                                        'coordinates': [geoObject['lon'], geoObject['lat']]
                                    },
                                    'display_name': geoObject['display_name'],
                                    'road': geoObject['address']['road'],
                                    'city': geoObject['address']['city'],
                                    'county': geoObject['address']['county'],
                                    'state': geoObject['address']['state'],
                                    'postcode': geoObject['address']['postcode'],
                                    'country': geoObject['address']['country'],
                                    'country_code': geoObject['address']['country_code'],
                                    'boundingbox': geoObject['boundingbox']
                                }
                                geocode_id = db.geocodes.insert_one(new_geocode).inserted_id

                                # now write the actual detection doc
                                print('for reference, the filename of the video is ')

                                post_data = {
                                    'plateContent': lp_str,
                                    'ts': detection_time,
                                    'cameraLocation': camera_location,
                                    'pollID': matching_poll['_id'],
                                    'location': matching_poll['location'],
                                    'driveID': matching_poll['driveID'] or undefined,
                                    'speed': matching_poll['speed'],
                                    'power': matching_poll['power'],
                                    'vyear': newVyear,
                                    'vmake': newVmake,
                                    'vmodel': newVmodel,
                                    'street': geoObject['address']['road'],
                                    'city': geoObject['address']['city'],
                                    'geocodeID': geocode_id,
                                    'heading': matching_poll['heading'],
                                    'status': matching_poll['status'],
                                    'detectionImgPath': event.src_path,
                                    'plateID': plate_id,
                                    'vehicleImgPath': '/tesladrive/detections/vehicles/%s.png' % '_'.join(
                                        file_name.split('_')[:-1]),
                                    'secondsIntoVideo': frame_time_seconds,
                                    'videoFileName': '/tesladrive/Videos/%s.mp4' % (
                                        '-'.join('_'.join(file_name.split('_')[:-2]).split(
                                            '-')[
                                                 :-1]))
                                }

                                result = plate_detections.insert_one(post_data)
                                print('One detection added: {0}'.format(result.inserted_id))

                                # update the matching poll doc
                                db.Doc.update({"_id": matching_poll["_id"]},
                                              {"$set": {'street': geoObject['address']['road'],
                                                        'city': geoObject['address']['city'],
                                                        'geocodeID': geocode_id, }})
                        else:
                            print("no matching poll found, entering a fake coordinate and marking to review later")
                            matching_poll = db.polls.find_one({"_id": ObjectId('5dabb930657f9d3e10178866')})
                            print(matching_poll)

                            # does the poll have a geocodeID?
                            ####geocode temp fix, for testing. everything in prod will have a street value
                            reqHeaders = {'User-Agent': 'SDScout/0.0.1'}
                            reqGeoCode = requests.get(
                                url='https://nominatim.openstreetmap.org/reverse?format=json&lat={}&lon={}&zoom=18&addressdetails=1'.format(
                                    matching_poll['location']['coordinates'][1],
                                    matching_poll['location']['coordinates'][0]), headers=reqHeaders)
                            print(reqGeoCode.json())
                            geoObject = reqGeoCode.json()
                            # reqGeoCode.json()[0]['year']

                            # now save geocode as it's own document for forward compatibility
                            new_geocode = {
                                'place_id': geoObject['place_id'],
                                'osm_type': geoObject['osm_type'],
                                'osm_id': geoObject['osm_id'],
                                'location': {
                                    'type': "Point",
                                    'coordinates': [geoObject['lon'], geoObject['lat']]
                                },
                                'display_name': geoObject['display_name'],
                                'road': geoObject['address']['road'],
                                'city': geoObject['address']['city'],
                                'county': geoObject['address']['county'],
                                'state': geoObject['address']['state'],
                                'postcode': geoObject['address']['postcode'],
                                'country': geoObject['address']['country'],
                                'country_code': geoObject['address']['country_code'],
                                'boundingbox': geoObject['boundingbox']
                            }
                            geocode_id = db.geocodes.insert_one(new_geocode).inserted_id

                            # update the matching poll doc
                            db.Doc.update({"_id": matching_poll["_id"]},
                                          {"$set": {'street': geoObject['address']['road'],
                                                    'city': geoObject['address']['city'],
                                                    'geocodeID': geocode_id, }})
                            ####end temp geocode fix

                            existing_plate = db.plates.find_one({"plateContent": lp_str})

                            if existing_plate:
                                print('plate exists!', existing_plate)
                                post_data = {
                                    'plateContent': lp_str,
                                    'ts': detection_time,
                                    'cameraLocation': camera_location,
                                    'pollID': matching_poll['_id'],
                                    'location': matching_poll['location'],
                                    'fakePoll': True,
                                    'driveID': ObjectId('5d3f848be08cfb4a873092db'),
                                    'speed': matching_poll['speed'],
                                    'street': geoObject['address']['road'],
                                    'city': geoObject['address']['city'],
                                    'geocodeID': geocode_id,
                                    'power': matching_poll['power'],
                                    'heading': matching_poll['heading'],
                                    'status': matching_poll['status'],
                                    'detectionImgPath': event.src_path,
                                    'plateID': existing_plate['_id'],
                                    'vyear': existing_plate['vyear'],
                                    'vmake': existing_plate['vmake'],
                                    'vmodel': existing_plate['vmodel'],
                                    'vehicleImgPath': '/tesladrive/detections/vehicles/%s.png' % '_'.join(
                                        file_name.split('_')[:-1]),
                                    'secondsIntoVideo': frame_time_seconds,
                                    'videoFileName': '/tesladrive/Videos/%s.mp4' % (
                                        '-'.join('_'.join(file_name.split('_')[:-2]).split(
                                            '-')[
                                                 :-1]))
                                }

                                result = plate_detections.insert_one(post_data)
                                print('One plate detection added: {0}'.format(result.inserted_id))

                            else:
                                # we need to create a doc in PLATES first, get that objectID, then add the plateDetection

                                # but first we need to do the make model lookup
                                session = requests.Session()
                                session.headers.update({
                                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:69.0) Gecko/20100101 Firefox/69.0'})
                                reqMakeModel = session.get(
                                    'https://www.carfax.com/api/mobile-homepage-quickvin-check?plate={}&state={}'.format(
                                        lp_str, homestate))

                                newVyear = '-'
                                newVmake = '-'
                                newVmodel = '-'
                                print(reqMakeModel.json())

                                try:
                                    newVyear = reqMakeModel.json()['quickVinResults'][0]['year']
                                    newVmake = reqMakeModel.json()['quickVinResults'][0]['make']
                                    newVmodel = reqMakeModel.json()['quickVinResults'][0]['model']
                                except:
                                    print('plate not found')

                                new_plate = {
                                    'plateContent': lp_str,
                                    'vyear': newVyear,
                                    'vmake': newVmake,
                                    'vmodel': newVmodel
                                }
                                plate_id = db.plates.insert_one(new_plate).inserted_id

                                # dont forget to add geocode

                                ####geocode temp fix, for testing. everything in prod will have a street value
                                # this is a parked detection so we need to get geocode
                                reqHeaders = {'User-Agent': 'SDScout/0.0.1'}
                                reqGeoCode = requests.get(
                                    url='https://nominatim.openstreetmap.org/reverse?format=json&lat={}&lon={}&zoom=18&addressdetails=1'.format(
                                        matching_poll['location']['coordinates'][1],
                                        matching_poll['location']['coordinates'][0]), headers=reqHeaders)
                                print(reqGeoCode.json())
                                geoObject = reqGeoCode.json()
                                # reqGeoCode.json()[0]['year']

                                # now save geocode as it's own document for forward compatibility
                                new_geocode = {
                                    'place_id': geoObject['place_id'],
                                    'osm_type': geoObject['osm_type'],
                                    'osm_id': geoObject['osm_id'],
                                    'location': {
                                        'type': "Point",
                                        'coordinates': [geoObject['lon'], geoObject['lat']]
                                    },
                                    'display_name': geoObject['display_name'],
                                    'road': geoObject['address']['road'],
                                    'city': geoObject['address']['city'],
                                    'county': geoObject['address']['county'],
                                    'state': geoObject['address']['state'],
                                    'postcode': geoObject['address']['postcode'],
                                    'country': geoObject['address']['country'],
                                    'country_code': geoObject['address']['country_code'],
                                    'boundingbox': geoObject['boundingbox']
                                }
                                geocode_id = db.geocodes.insert_one(new_geocode).inserted_id

                                # now write the actual detection doc
                                print('for reference, the filename of the video is ')

                                post_data = {
                                    'plateContent': lp_str,
                                    'ts': detection_time,
                                    'cameraLocation': camera_location,
                                    'pollID': matching_poll['_id'],
                                    'location': matching_poll['location'],
                                    'driveID': ObjectId('5d3f848be08cfb4a873092db'),
                                    'speed': matching_poll['speed'],
                                    'power': matching_poll['power'],
                                    'vyear': newVyear,
                                    'vmake': newVmake,
                                    'vmodel': newVmodel,
                                    'street': geoObject['address']['road'],
                                    'city': geoObject['address']['city'],
                                    'geocodeID': geocode_id,
                                    'heading': matching_poll['heading'],
                                    'status': matching_poll['status'],
                                    'detectionImgPath': event.src_path,
                                    'plateID': plate_id,
                                    'vehicleImgPath': '/tesladrive/detections/vehicles/%s.png' % '_'.join(
                                        file_name.split('_')[:-1]),
                                    'secondsIntoVideo': frame_time_seconds,
                                    'videoFileName': '/tesladrive/Videos/%s.mp4' % (
                                        '-'.join('_'.join(file_name.split('_')[:-2]).split(
                                            '-')[
                                                 :-1]))
                                }

                                result = plate_detections.insert_one(post_data)
                                print('One detection added: {0}'.format(result.inserted_id))

                                # update the matching poll doc
                                db.Doc.update({"_id": matching_poll["_id"]},
                                              {"$set": {'street': geoObject['address']['road'],
                                                        'city': geoObject['address']['city'],
                                                        'geocodeID': geocode_id, }})

                    else:
                        print('plate detected too short, likely false positive: ', lp_str)
                        if os.path.exists(img_path):
                            os.remove(img_path)
                        # remove vehicle image as well
                        vehicleImgPath = img_path.rsplit('_', 1)[0].replace("plates", "vehicles") + '.png'
                        if os.path.exists(vehicleImgPath):
                            os.remove(vehicleImgPath)
                        print('removing {} and {}'.format(img_path, vehicleImgPath))

                else:
                    print('No characters found')
                    if os.path.exists(img_path):
                        os.remove(img_path)
                    # remove vehicle image as well
                    vehicleImgPath = img_path.rsplit('_', 1)[0].replace("plates", "vehicles") + '.png'
                    if os.path.exists(img_path):
                        os.remove(vehicleImgPath)
                    print('removing {} and {}'.format(img_path, vehicleImgPath))

            except:
                traceback.print_exc()
                sys.exit(1)

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            print("Received modified event - %s." % event.src_path)


if __name__ == '__main__':
    w = Watcher()
    w.run()

