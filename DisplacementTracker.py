import cv2
import numpy as np
import csv

filename=input("File Name: ")
path="*/DisplacementTracker/Video/"+filename
framerate=24
cap = cv2.VideoCapture(path)
ret = True #Value to see if frame exists
while ret:
    ret, img = cap.read() # read one frame from the 'capture' object; img is (H, W, C)
    if ret:
        frames.append(img)
video = np.stack(frames, axis=0)
time=[]
x=[]
y=[]
csvfilename=filename.split('.')[0]+'.csv'
