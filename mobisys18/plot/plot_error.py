import numpy as np
import cv2
import sys
import time
import datetime
import itertools as it
import hashlib
import pickle
import os


class Evaluator(object):
    def __init__(self, video_file):
        self._frame_index = 0
        self._click_pt = []
        self._clicking = False
        self._window_name = "SnapLink Analytics Tool"

        print "Reading the video..."
        self._frames = []
        self._read_frames(video_file)

        self._truth_locs = [[(-1, -1), False]] * len(self._frames) # x, y, isManual (False means derived from optical flow)

        print "Trying to read labels..."
        self._label_locs = self._read_data(video_file, "label_locs")
        if self._label_locs is None or len(self._label_locs) != len(self._frames):
            print "Reading failed, detecting labels..."
            self._label_locs = []
            self._detect_label_locs()
            self._write_data(video_file, self._label_locs, "label_locs")

        print "Trying to read optical flows..."
        self._flows = self._read_data(video_file, "flows")
        if self._flows is None or len(self._flows) != len(self._frames) - 1:
            print "Reading failed, computing optical flows..."
            self._flows = []
            self._compute_flows()
            self._write_data(video_file, self._flows, "flows")

        print self._flows[0].shape
        cv2.namedWindow(self._window_name)
        cv2.createTrackbar('track_bar', self._window_name, self._frame_index, len(self._frames) - 1, self._on_change)
        cv2.setMouseCallback(self._window_name, self._on_click)

    def _read_frames(self, video_file):
        cap = cv2.VideoCapture(video_file)
        while cap.isOpened():
            ret, frame = cap.read()
            if ret is True:
                self._frames.append(frame)
            else:
                break
        cap.release()
    
    def _detect_label_locs(self):
        size = 140
        template = np.zeros(shape=(size, size), dtype=np.uint8)
        cv2.rectangle(template, pt1=(0, 0), pt2=(size, size), color=255, thickness=5)
    
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
        t0 = time.time()
        for i in range(len(self._frames) - 1):
            prev_frame = frames_gray[i]
            next_frame = frames_gray[i + 1]
            flow = cv2.calcOpticalFlowFarneback(prev_frame, next_frame, flow=None, pyr_scale=0.5, levels=3, winsize=15, iterations=3, poly_n=5, poly_sigma=1.1, flags=0)
            self._flows.append(flow)
    
            t1 = time.time()
            time_remain = datetime.timedelta(seconds=int((t1 - t0)/(i + 1)*(len(self._frames) - 1 - (i + 1))))
            print  "\rProcessing frame {0}/{1}, {2} remaining".format(i + 1, len(self._frames) - 1, time_remain),
    
        print ""
    
    def _read_data(self, video_file, label):
        data_file = hashlib.md5(open(video_file, 'rb').read()).hexdigest() + "." + label
        data = None
        if os.path.exists(data_file):
            with open(data_file, 'rb') as f:
                data = pickle.load(f)
        return data
    
    def _write_data(self, video_file, data, label):
        data_file = hashlib.md5(open(video_file, 'rb').read()).hexdigest() + "." + label
        with open(data_file, 'wb') as f:
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
    
    def _on_change(self, x):
        self._frame_index = x
        self._refresh_ui()
    
    def _update_truth_locs(self):
        self._truth_locs[self._frame_index][0] = self._click_pt
        self._truth_locs[self._frame_index][1] = True 
        for i in range(self._frame_index, len(self._flows)):
            flow = self._flows[i]
            print self._frame_index, self._truth_locs[i]
            x, y = self._truth_locs[i][0]
            is_manual = self._truth_locs[i + 1][1]
            if is_manual == True: # only use optical flow if next one was not manually labeled
                break
            else:
                print "updating frame ", i + 1
                self._truth_locs[i + 1][0] = (x + flow[y, x][0], y + flow[y, x][1])
    
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
    Evaluator(sys.argv[1]).run()
