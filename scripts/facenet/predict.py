from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# ----------------------------------------------------
# MIT License
#
# Copyright (c) 2017 Rishi Rai
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ----------------------------------------------------

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tensorflow as tf
import numpy as np
import argparse
import cv2
import facenet
import os
import sys
import math
import pickle
from sklearn.svm import SVC
from scipy import misc
import align.detect_face
from six.moves import xrange
from shutil import copyfile
import datetime
import pytz
from pymongo import MongoClient

uri = "CHANGEME"
client = MongoClient(uri)
db = client.sds_db
face_detections = db.faceDetections
from bson.objectid import ObjectId

with tf.Graph().as_default():
    sess = tf.Session()
    # Load the model
    facenet.load_model("/home/CHANGEME(USERNAME)/models/facenet/20180402-114759/20180402-114759.pb")
    # Get input and output tensors
    images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
    embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
    phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")

    # Run forward pass to calculate embeddings

    classifier_filename_exp = os.path.expanduser("/home/CHANGEME(USERNAME)/models/my_classifier.pkl")
    with open(classifier_filename_exp, 'rb') as infile:
        (model, class_names) = pickle.load(infile)
    print('Loaded classifier model from file "%s"\n' % classifier_filename_exp)
    minsize = 20  # minimum size of face
    threshold = [0.6, 0.7, 0.7]  # three steps's threshold
    factor = 0.709  # scale factor

    print('Creating networks and loading parameters')
    with tf.Graph().as_default():
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.6)
        sess2 = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
        with sess2.as_default():
            pnet, rnet, onet = align.detect_face.create_mtcnn(sess2, None)
    print("done loading networks")


def load_and_align_data(image_paths, image_size, margin, gpu_memory_fraction):
    nrof_samples = len(image_paths)
    img_list = []
    count_per_image = []
    img = misc.imread(image_paths)
    img_size = np.asarray(img.shape)[0:2]
    bounding_boxes, _ = align.detect_face.detect_face(img, minsize, pnet, rnet, onet, threshold, factor)
    count_per_image.append(len(bounding_boxes))

    for j in range(len(bounding_boxes)):
        det = np.squeeze(bounding_boxes[j, 0:4])
        bb = np.zeros(4, dtype=np.int32)
        bb[0] = np.maximum(det[0] - margin / 2, 0)
        bb[1] = np.maximum(det[1] - margin / 2, 0)
        bb[2] = np.minimum(det[2] + margin / 2, img_size[1])
        bb[3] = np.minimum(det[3] + margin / 2, img_size[0])
        cropped = img[bb[1]:bb[3], bb[0]:bb[2], :]
        aligned = misc.imresize(cropped, (image_size, image_size), interp='bilinear')
        prewhitened = facenet.prewhiten(aligned)
        newName = "/tesladrive/detections/faces/{}".format(image_paths).split('/')[-1]
        cv2.imwrite("/tesladrive/detections/faces/{}".format(newName), cv2.cvtColor(aligned, cv2.COLOR_BGR2RGB))
        print('wrote face to file: ', "/tesladrive/detections/faces/{}".format(newName))
        img_list.append(prewhitened)
    images = np.stack(img_list)
    return images, count_per_image, nrof_samples


class Watcher:
    DIRECTORY_TO_WATCH = "/tesladrive/detections/people"

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
            images, count_per_image, nrof_samples = load_and_align_data(event.src_path, 160, 44, 0.6)
            feed_dict = {images_placeholder: images, phase_train_placeholder: False}
            emb = sess.run(embeddings, feed_dict=feed_dict)
            predictions = model.predict_proba(emb)
            best_class_indices = np.argmax(predictions, axis=1)
            best_class_probabilities = predictions[np.arange(len(best_class_indices)), best_class_indices]
            k = 0
            # print predictions
            filename_full = os.path.basename(event.src_path)
            print('%s: %.3f' % (class_names[best_class_indices[k]], best_class_probabilities[k]))
            # mongo lookups and writes here
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
            video_filename = "/tesladrive/Videos/{}.mp4".format("-".join("_"
                                                                           .join(file_name.split("_")[:-1]).split("-")[
                                                                           :-1]))

            # if probability is below x amount, it's a new face. initially, we should load with LFW faces that way we can start out with at least something to compare to. if we start out with only one face (the initial detection) it will always say it's that face. so, we could say if top stranger is a celeb (from lfw), it's unknown face.

            # get predictionID

            matching_poll = db.polls.find_one({"unixTS": detection_time})
            if matching_poll:
                print(matching_poll)
                onDrive = False

                try:
                    if matching_poll['driveID']:
                        onDrive = True
                        print('detection occured during a drive')
                except:
                    print('detection occured while parked, do not add driveID in object')

                if "sample" in class_names[best_class_indices[k]]:
                    # it's a new face
                    # create a new face,
                    new_face = {
                        'personName': 'Stranger #{}'.format(db.faces.find().count() + 1),
                        'notNamed': True
                    }
                    face_id = db.faces.insert_one(new_face).inserted_id
                    # get the faceID
                    # write a faceDetection doc
                    post_data = {
                        'ts': detection_time,
                        'notNamed': True,
                        'personName':'Stranger #{}'.format(db.faces.find().count()),
                        'cameraLocation': camera_location,
                        'pollID': matching_poll['_id'],
                        'location': matching_poll['location'],
                        'speed': matching_poll['speed'],
                        'power': matching_poll['power'],
                        'heading': matching_poll['heading'],
                        'status': matching_poll['status'],
                        'detectionImgPath': '/tesladrive/detections/faces/%s' % filename_full,
                        'faceID': face_id,
                        'personImgPath': event.src_path,
                        'secondsIntoVideo': frame_time_seconds,
                        'videoFileName': video_filename
                    }
                    try:
                        post_data['street'] = matching_poll['street']
                        post_data['city'] = matching_poll['city']
                        post_data['geocodeID'] = matching_poll['geocodeID']
                    except:
                        print('noGeocode for the poll')
                        
                    if onDrive:
                        post_data['driveID'] = matching_poll['driveID']

                    result = face_detections.insert_one(post_data)
                    print('One face detection added: {0}'.format(result.inserted_id))

                    # create the training directory
                    newFacePath = "/tesladrive/datasets/scout/train/{}".format(str(face_id))
                    os.mkdir(newFacePath)
                    print('created new training folder: ', newFacePath)
                    # now, copy face image into that folder for retraining

                    copyfile('/tesladrive/detections/faces/{}'.format(filename_full), '{}/{}.png'.
                             format(newFacePath, str(result.inserted_id)))

                else:
                    # check if probability above 60%
                    if best_class_probabilities[k] > 0.55:
                        matching_person = db.polls.find_one({"_id": ObjectId(class_names[best_class_indices[k]])})
                        # likely a real match
                        # face already exists
                        # write a faceDetection doc
                        post_data = {
                            'ts': detection_time,
                            'personName':matching_person['personName'],
                            'notNamed':False,
                            'cameraLocation': camera_location,
                            'pollID': matching_poll['_id'],
                            'location': matching_poll['location'],
                            'speed': matching_poll['speed'],
                            'power': matching_poll['power'],
                            'heading': matching_poll['heading'],
                            'status': matching_poll['status'],
                            'detectionImgPath': '/tesladrive/detections/faces/%s' % filename_full,
                            'faceID': ObjectId(class_names[best_class_indices[k]]),
                            'personImgPath': event.src_path,
                            'secondsIntoVideo': frame_time_seconds,
                            'videoFileName': video_filename
                        }
                        try:
                            post_data['street'] = matching_poll['street']
                            post_data['city'] = matching_poll['city']
                            post_data['geocodeID'] = matching_poll['geocodeID']
                        except:
                            print('noGeocode for the poll')
                            
                        if onDrive:
                            post_data['driveID'] = matching_poll['driveID']

                        result = face_detections.insert_one(post_data)
                        print('One face detection added: {0}'.format(result.inserted_id))
                        copyfile('/tesladrive/detections/faces/{}'.format(filename_full),
                                 '/tesladrive/datasets/scout/train/{}/{}.png'.format(class_names[best_class_indices[k]],
                                                                                     str(result.inserted_id)))

                    else:
                        # treat as new face
                        new_face = {
                            'personName': 'Stranger #{}'.format(db.faces.find().count() + 1),
                            'notNamed': True
                        }
                        face_id = db.faces.insert_one(new_face).inserted_id
                        # get the faceID
                        # write a faceDetection doc
                        post_data = {
                            'ts': detection_time,
                            'personName': 'Stranger #{}'.format(db.faces.find().count()),
                            'notNamed': True,
                            'cameraLocation': camera_location,
                            'pollID': matching_poll['_id'],
                            'location': matching_poll['location'],
                            'speed': matching_poll['speed'],
                            'power': matching_poll['power'],
                            'heading': matching_poll['heading'],
                            'status': matching_poll['status'],
                            'detectionImgPath': '/tesladrive/detections/faces/%s' % filename_full,
                            'faceID': face_id,
                            'personImgPath': event.src_path,
                            'secondsIntoVideo': frame_time_seconds,
                            'videoFileName': video_filename
                        }
                        try:
                            post_data['street'] = matching_poll['street']
                            post_data['city'] = matching_poll['city']
                            post_data['geocodeID'] = matching_poll['geocodeID']
                        except:
                            print('noGeocode for the poll')

                        if onDrive:
                            post_data['driveID'] = matching_poll['driveID']

                        result = face_detections.insert_one(post_data)
                        print('One face detection added: {0}'.format(result.inserted_id))

                        # create the training directory
                        newFacePath = "/tesladrive/datasets/scout/train/{}".format(str(face_id))
                        os.mkdir(newFacePath)
                        print('created new training folder: ', newFacePath)

                        # copy the face image over
                        # now, copy face image into that folder for retraining
                        # folder should be faceID, imagename should be detectionID.png
                        copyfile('/tesladrive/detections/faces/{}'.format(filename_full), '{}/{}.png'.
                                 format(newFacePath, str(result.inserted_id)))

            else:
                print("no matching poll found")

            k += 1


if __name__ == '__main__':
    w = Watcher()
    w.run()

