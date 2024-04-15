import cv2
import numpy as np
import csv
import os
from PIL import Image

#Black box function to convert a single color into a range of colors
def color(color):
  c=np.uint8([[color]])
  hsvC=cv2.cvtColor(c,cv2.COLOR_BGR2HSV)
  lowerlimit=hsvC[0][0][0]-10,100,100
  upperlimit=hsvC[0][0][0]+10,255,255
  lowerlimit=np.array(lowerlimit, dtype=np.uint8)
  upperlimit=np.array(upperlimit, dtype=np.uint8)
  return [lowerlimit, upperlimit]

filename=input("Include File Extension\nFile Name: ") #Get file name from user
path=os.path.abspath('DisplacementTracker')+'\\Video\\'+filename #Create path from file name

''''''
#Pre-defined parameters defined in code for ease of repitive operation
boxwidth=5 #Width of target box in mm
framerate=30 #Variable depending on camera
width=1920#Frame width (pixels)
height=1080#Frame height (pixels)
''''''

cap = cv2.VideoCapture(path) #Define video capture object
ret = True #Value to see if frame exists
#Create array of frames

cords=[]#Pre-define cords array to write to .csv file later
framecount=0#Pre-define framecount to use to check time
red=[255,0,0]#Define RGB colorspace for red
green=[0,255,0]#Define RGB colorspace for green

#Write each frame with added elements to video file
fourcc=cv2.VideoWriter_fourcc(*'MP42')
video=cv2.VideoWriter(filename+'ANALYZED.avi',fourcc, float(framerate), (width,height))
directory=os.path.abspath('DisplacementTracker')+'\\Video\\'
list=os.listdir(directory)

# Read until video is completed
while True:
  ret,frame=cap.read()
  # Capture frame-by-frame
  if ret == True:
    hsv=cv2.cvtColor(frame,cv2.COLORBGR2HSV)#Convert frame to hue color gradient
    redmask=cv2.inRange(hsv,color(color=red)[0], color(color=red)[1])#Turn only red pixels in range white and the rest black
    greenmask=cv2.inRange(hsv,color(color=green)[0], color(color=green)[1])#Turn only green pixels in range white and the rest black
    redmask_=Image.fromarray(redmask)#Convert redmask to Image array
    greenmask_=Image.fromarray(greenmask)#Convert greenmask to Image array
    redbbox=redmask_.getbbox()#Create array of 4 values defining x,y, width and height of bounding box over red box
    greenbbox=greenmask_.getbbox()#Create array of 4 values defining x,y, width and height of bounding box over green box
    pixel_to_mm=((boxwidth/redbbox[3])+(boxwidth/redbbox[4])+(boxwidth/greenbbox[3])+(boxwidth/greenbbox[4]))/4#5mm/box width or height. Take average of width and height of red and green box for more accurate conversion
    redcords=redbbox*pixel_to_mm
    greencords=greenbbox*pixel_to_mm
    cv2.rectangle(frame,(redcords[0],redcords[1]),((redcords[0]+redcords[2]),(redcords[1]+redcords[3])),(255,0,0))#Put a rectangle around the red box in the video
    cv2.rectangle(frame,(greencords[0],greencords[1]),((greencords[0]+greencords[2]),(greencords[1]+greencords[3])),(0,255,0))#Put a rectangle around the green box in the video
    red_x_center=redcords[0]+(redcords[2]/2)#The x & y coordinates give the coordinates to a corner, so use width/height to find center of box
    #The x & y coordinates give the coordinates to a corner, so use width/height to find center of box
    red_y_center=redcords[1]+(redcords[3]/2)
    green_x_center=greencords[0]+(greencords[2]/2)
    green_y_center=greencords[1]+(greencords[3]/2)
    cv2.circle(frame, (red_x_center,red_y_center), 1.5*pixel_to_mm, (255,0,0),pixel_to_mm)#Create a 1.5mm radius 1mm thick red circle inside the red box (ensures proper calculations)
    cv2.circle(frame, (green_x_center,green_y_center), 1.5*pixel_to_mm, (0,255,0),pixel_to_mm)#Create a 1.5mm radius 1mm thick green circle inside the red box
    time=framecount/framerate #Frame count used with framerate to tell time
    y_displacement=abs(red_y_center-green_y_center)#Absolute value due to the unknown location of the green and red markers
    cords.append([red_x_center, red_y_center,green_x_center,green_y_center, y_displacement, time])#red_x_center,red_y_center,green_x_center,green_y_center,y_displacement, time
    video.write(frame)#Add this frame to video
    framecount+=1
  # Break the loop
  else: 
    break
cap.release()
video.release()

csvfilename=filename.split('.')[0]+'.csv'#Write .csv filename as name of video .csv
fields=['Red_X_Center','Red_Y_center','Green_X_Center','Green_Y_Center','Y_Displacement','Time'] #Field values of each column of .csv file
with open(csvfilename, 'w') as csvfile:
  writer=csv.DictWriter(csvfile,fieldnames=fields)
  writer=writerheader()#Write header of fields
  writer.writerows(cords)#Add all values to .csv file
