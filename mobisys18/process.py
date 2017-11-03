import numpy as np
import cv2
import sys
import time
import itertools as it

def get_template(shape):
    template = np.zeros(shape=shape, dtype=np.uint8)
    cv2.rectangle(template, pt1=(0, 0), pt2=shape, color=255, thickness=5)
    return template

def loc_label(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower = np.array([115, 30, 30])
    upper = np.array([125, 255, 255])
    filtered = cv2.inRange(hsv, lower, upper)

    size = 140
    template = get_template(shape=(size, size))
    matched = cv2.matchTemplate(filtered, template, method=cv2.TM_CCORR)

    _, _, _, max_loc = cv2.minMaxLoc(matched)
    label_loc = tuple(x + size/2 for x in max_loc)

    return label_loc

def read_frames(video_file):
    print "Processing the video..."
    frames = []
    label_locs = []
    cap = cv2.VideoCapture(video_file)
    while cap.isOpened():
        ret, frame = cap.read()
        if ret is True:
            label_loc = loc_label(frame)
            frames.append(frame)
            label_locs.append(label_loc)
        else:
            break
    cap.release()
    return frames, label_locs

frame_index = 0
def on_change(x):
    global frame_index
    frame_index = x

video_file = sys.argv[1]
frames, label_locs = read_frames(video_file)
cv2.namedWindow('image')
cv2.createTrackbar('R', 'image', 1, len(frames), on_change)
while True:
    frame = frames[frame_index]
    cv2.circle(frame, label_locs[frame_index], 5, (255, 0, 0), 2)
    cv2.imshow('image', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
