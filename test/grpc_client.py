#!/usr/bin/env python

from __future__ import division

import grpc
import subprocess
import glob
import os
import sys
import numpy as np
import cv2
import time
from PIL import Image, ExifTags

currentDir = dir_path = os.path.dirname(os.path.realpath(__file__))
rootDir = currentDir+"/../"
subprocess.call(["python", "-m", "grpc_tools.protoc", "-I="+ rootDir + "/src/proto/", "--python_out=" + currentDir, "--grpc_python_out=" + currentDir , rootDir + "/src/proto/GrpcService.proto"])

import GrpcService_pb2
import GrpcService_pb2_grpc


SERVER_ADDR = "0.0.0.0:8080"

RESULT_PASS = 0
RESULT_BAD_FORMAT = 1
RESULT_FAIL = 2

def test_file(filename, stub):
    obj_name = os.path.basename(filename).split(".")[0]

    img = Image.open(filename)
    width, height = img.size
    img.thumbnail((width, height), Image.ANTIALIAS)

    img = img.convert('L') # convert to grayscale

    img = np.array(img) # convert from PIL image to OpenCV image

    _, jpg = cv2.imencode('.jpg', img)

    print filename, 'width:', width, 'height:', height
    
    t0 = time.time()
    request = GrpcService_pb2.LocalizationRequest(image=jpg.tostring(), orientation = 1)
    request.camera.fx=562.25
    request.camera.fy=562.25
    request.camera.cx=240
    request.camera.cy=320
    rIter = stub.localize(iter([request]))
    r = rIter.next()
    t1 = time.time()
    elapsed_time = round((t1 - t0)*1000, 2)
    if len(r.items) == 0:
        text = "test failed. response = None, obj = {0}, elapsed time = {1} milliseconds".format(obj_name, elapsed_time)
        print text
        return RESULT_FAIL, elapsed_time
    if r.items[0].name != obj_name:
        text = "test failed. response = {0}, obj = {1}, elapsed time = {2} milliseconds".format(r.items[0].name, obj_name, elapsed_time)
        print text
        return RESULT_FAIL, elapsed_time
    else:
        print "test passed. response = {0}, obj = {1}, elapsed time = {2} milliseconds".format(r.items[0].name, obj_name, elapsed_time)
        return RESULT_PASS, elapsed_time


def test_dir(directory, stub):
    pass_count = 0
    bad_format_count = 0
    fail_count = 0
    elapsed_times = []
    for filename in glob.glob(os.path.join(directory, "*")):
        if not filename.endswith(".jpg") and not filename.endswith(".JPG"):
            continue
        result, elapsed_time = test_file(filename, stub)
        if result == RESULT_PASS:
            pass_count += 1
        elif result == RESULT_BAD_FORMAT:
            bad_format_count += 1
        elif result == RESULT_FAIL:
            fail_count += 1
        elapsed_times.append(elapsed_time)
    if elapsed_times:
        elapsed_times = np.array(elapsed_times)
        print "{0}/{1} tests passed, {2} bad format, mean time {3} +/- {4}".format(pass_count, pass_count+fail_count, bad_format_count, round(np.mean(elapsed_times), 2), round(np.std(elapsed_times), 2))
    else:
        print "No image found"

if __name__ == "__main__":
    channel = grpc.insecure_channel(SERVER_ADDR)
    stub = GrpcService_pb2_grpc.GrpcServiceStub(channel)
    
    if len(sys.argv) == 2:
        path = sys.argv[-1]
        if os.path.isdir(path):
            test_dir(path, stub)
        elif os.path.isfile(path):
            test_file(path, stub)
        else:
            print "Invalid path"
    else:
        print "Please provide image directory"
