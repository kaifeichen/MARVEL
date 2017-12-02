import numpy as np
import cv2
import sys
import time
import datetime
import itertools as it
import hashlib
import pickle
import os


def read_data(data_file):
    data = None
    if os.path.exists(data_file):
        with open(data_file, 'rb') as f:
            data = pickle.load(f)
    return data

def write_data(data, data_file):
    with open(data_file, 'wb') as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

class Labeler(object):
    def __init__(self, video_file):
        self._frame_index = 0
        self._click_pt = []
        self._clicking = False
        self._window_name = "SnapLink Analytics Tool"
        self._video_file = video_file
        self._file_hash = hashlib.md5(open(self._video_file, 'rb').read()).hexdigest()

        print "Reading the video..."
        self._frames = []
        self._read_frames()

        print "Trying to read truth locations..."
        self._truth_locs = read_data("." + self._file_hash + ".truth_locs")
        if self._truth_locs is None or len(self._truth_locs) != len(self._frames):
            print "Reading failed, resetting truth locs..."
            self._truth_locs = [[(-1, -1), False] for _ in range(len(self._frames))] # x, y, isManual (False means derived from optical flow)
            write_data(self._truth_locs, "." + self._file_hash + ".truth_locs")

        print "Trying to read labels..."
        self._label_locs = read_data("." + self._file_hash + ".label_locs")
        if self._label_locs is None or len(self._label_locs) != len(self._frames):
            print "Reading failed, detecting labels..."
            self._label_locs = []
            self._detect_label_locs()
            write_data(self._label_locs, "." + self._file_hash + ".label_locs")

        print "Trying to read optical flows..."
        self._flows = read_data("." + self._file_hash + ".flows")
        if self._flows is None or len(self._flows) != len(self._frames) - 1:
            print "Reading failed, computing optical flows..."
            self._flows = []
            self._compute_flows()
            write_data(self._flows, "." + self._file_hash + ".flows")

        cv2.namedWindow(self._window_name)
        cv2.createTrackbar('track_bar', self._window_name, self._frame_index, len(self._frames) - 1, self._on_change)
        cv2.setMouseCallback(self._window_name, self._on_click)

    def _read_frames(self):
        cap = cv2.VideoCapture(self._video_file)
        while cap.isOpened():
            ret, frame = cap.read()
            if ret is True:
                self._frames.append(frame)
            else:
                break
        cap.release()
    
    def _detect_label_locs(self):
        size = 35
        template = np.zeros(shape=(size, size), dtype=np.uint8)
        cv2.circle(template, center=(3,3), radius=3, color=255, thickness=-1)
        cv2.circle(template, center=(32,32), radius=3, color=255, thickness=-1)
        cv2.circle(template, center=(3,32), radius=3, color=255, thickness=-1)
        cv2.circle(template, center=(32,3), radius=3, color=255, thickness=-1)
        #cv2.rectangle(template, pt1=(0, 0), pt2=(size, size), color=255, thickness=5)

    
        t0 = time.time()
        for i in range(len(self._frames)):
            frame = self._frames[i]
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower = np.array([115, 30, 30])
            upper = np.array([125, 255, 255])
            filtered = cv2.inRange(hsv, lower, upper)
            matched = cv2.matchTemplate(filtered, template, method=cv2.TM_CCORR)
            _, _, _, max_loc = cv2.minMaxLoc(matched)
            label_loc = tuple(x + size/2 for x in max_loc)
            self._label_locs.append(label_loc)
    
            t1 = time.time()
            time_remain = datetime.timedelta(seconds=int((t1 - t0)/(i + 1)*(len(self._frames) - (i + 1))))
            print  "\rProcessing frame {0}/{1}, {2} remaining".format(i + 1, len(self._frames), time_remain),
    
        print ""
    
    def _compute_flows(self):
        frames_gray = [cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) for frame in self._frames]

        feature_params = dict(maxCorners = 100,
                              qualityLevel = 0.3,
                              minDistance = 7,
                              blockSize = 7)
        lk_params = dict(winSize  = (15,15),
                         maxLevel = 2,
                         criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

        t0 = time.time()
        for i in range(len(self._frames) - 1):
            prev_gray = frames_gray[i]
            next_gray = frames_gray[i + 1]
            p0 = cv2.goodFeaturesToTrack(prev_gray, mask = None, **feature_params)
            p1, st, err = cv2.calcOpticalFlowPyrLK(prev_gray, next_gray, p0, None, **lk_params)
            good_old = p0[st==1]
            good_new = p1[st==1]
            self._flows.append((good_old, good_new))
    
            t1 = time.time()
            time_remain = datetime.timedelta(seconds=int((t1 - t0)/(i + 1)*(len(self._frames) - 1 - (i + 1))))
            print  "\rProcessing frame {0}/{1}, {2} remaining".format(i + 1, len(self._frames) - 1, time_remain),
    
        print ""
    
    def _on_change(self, x):
        self._frame_index = x
        self._refresh_ui()
    
    def _update_truth_locs(self):
        self._truth_locs[self._frame_index][0] = self._click_pt
        self._truth_locs[self._frame_index][1] = True 
        for i in range(self._frame_index, len(self._flows)):
            old, new = self._flows[i]
            x, y = self._truth_locs[i][0]
            is_next_manual = self._truth_locs[i + 1][1]
            if is_next_manual == True: # only use optical flow if next one was not manually labeled
                print "next frame {0} manually labelled, stop truth location computation".format(i + 1)
                break
            print "updating truth location on frame ", i + 1
            pairs = list(filter(lambda p: np.linalg.norm(p[0]-np.array((x, y))) < 300, zip(old, new)))
            pairs = sorted(pairs, key=lambda p: np.linalg.norm(p[0]-np.array((x, y))), reverse=True)
            offsets = []
            if len(pairs) == 0:
                break
            for pair in pairs:
                offsets.append(pair[1] - pair[0])
            offset = np.mean(offsets, axis=0).astype(int)
            print offset
            self._truth_locs[i + 1][0] = (x + offset[0], y + offset[1])
        write_data(self._truth_locs, "." + self._file_hash + ".truth_locs")
    
    def _on_click(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self._click_pt = (int(x), int(y))
            self._clicking = True
        elif event == cv2.EVENT_LBUTTONUP and self._clicking == True:
            self._update_truth_locs()
            self._click_pt = (-1, -1)
            self._clicking = False
            self._refresh_ui()
    
    def _refresh_ui(self):
        frame = self._frames[self._frame_index].copy()
        cv2.circle(frame, self._label_locs[self._frame_index], 5, (255, 0, 0), 2)
        if self._truth_locs[self._frame_index][0] != (-1, -1):
            cv2.circle(frame, self._truth_locs[self._frame_index][0], 5, (0, 0, 255), 2)
        cv2.imshow(self._window_name, frame)

    def run(self):
        self._refresh_ui()
        while True:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()

if __name__ == "__main__":
    Labeler(sys.argv[1]).run()
