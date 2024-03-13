import pathlib
import cv2
import numpy as np
import webcolors
import datetime
import easyocr
from pytesseract import pytesseract
import math

import googletrans
from googletrans import *


def scan_video_content(id):

    #reader = easyocr.Reader(['ar','en'])

    # Get the path to the xml file that holds the info for the face detection training (included in OpenCV)
    cascade_path = pathlib.Path(cv2.__file__).parent.absolute() / "data/haarcascade_frontalface_default.xml"
    # Construct the face detection classifier with the accessed xml file
    clf = cv2.CascadeClassifier(str(cascade_path))
    # Open a video file with OpenCV
    video = cv2.VideoCapture(f"videos/video_{id}.mp4")

    facial_presence = 0

    frame_number = 0
    
    rgb_list = []
    brightness_list = []

    previous_frame_text = ''
    current_frame_text = ''
    total_screen_text = ''

    # Read until video is completed
    while(video.isOpened()):
        # Capture video frame by frame
        ret, frame = video.read()
        print(f"Capturing frame {frame_number}...")
        # If the video capture detects a frame (i.e. we have not reached the end of the video)
        if ret == True:
            # Store grayscale version of current frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Store HSV (hue, saturation, value) version of current frame 
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            # Calculate facial presence
            faces = clf.detectMultiScale(
                gray,
                scaleFactor=1.4,
                minNeighbors=6,
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            #facial_presence += len(faces)
            if (len(faces) > 0):
                facial_presence += 1
            
            # for (x, y, width, height) in faces:
            #     cv2.rectangle(frame, (x, y), (x+width, y+height), (255, 255, 0), 2)

            # cv2.imshow("Faces", frame)
                

            # Dominant color detection
            height, width, _ = np.shape(frame)
            # print(height, width)

            data = np.reshape(frame, (height * width, 3))
            data = np.float32(data)

            number_clusters = 2
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            flags = cv2.KMEANS_RANDOM_CENTERS
            compactness, labels, centers = cv2.kmeans(data, number_clusters, None, criteria, 10, flags)
            # print(centers[0])
            # Convert openCV's BGR format to RGB
            this_rgb = [centers[0][2], centers[0][1], centers[0][0]]
            print(this_rgb)
            rgb_list.append(this_rgb)

            # Calculate brightness
            avg_bright = np.mean(hsv[:,:, 2])
            bright_percent = (avg_bright/255)*100
            brightness_list.append(bright_percent)

            #image2 = cv2.addWeighted(frame, 2, frame, 2, 0) 
            current_frame_text = pytesseract.image_to_string(frame, lang='ara+eng')
            
            # screen_text = reader.readtext(gray)
            # current_frame_text = ''
            # for i in screen_text:
            #     current_frame_text = current_frame_text + i[1] + '\n'
                #print(i[1])
            

            print(current_frame_text)
            print("-----")
            print(previous_frame_text)
            print("-----")
            print(current_frame_text != previous_frame_text)
            print("------")
            if not(current_frame_text == previous_frame_text):
                total_screen_text = total_screen_text + current_frame_text
            
            previous_frame_text = current_frame_text
            print(total_screen_text)

            # Add to the number of frames in order to calculate facial presence ratio
            frame_number += 5
            video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        # Break the loop when video is finished
        else:
            break

    # Calculate average dominant color
    avg_red, avg_green, avg_blue = 0, 0, 0       
    for color in rgb_list:
        avg_red += color[0]
        avg_green += color[1]
        avg_blue += color[2]
    avg_red /= len(rgb_list)
    avg_green /= len(rgb_list)
    avg_blue /= len(rgb_list)
    avg_rgb = (math.floor(avg_red), math.floor(avg_green), math.floor(avg_blue))

    # Calculate video duration
    frames = video.get(cv2.CAP_PROP_FRAME_COUNT) 
    fps = video.get(cv2.CAP_PROP_FPS)
    seconds = round(frames / fps) 
    video_time = str(datetime.timedelta(seconds=seconds))

    # Calculate brightness
    avg_bright = 0
    for i in brightness_list:
        avg_bright += i
    avg_bright /= len(brightness_list)

    for element in current_frame_text:
        if element == '\n':
            element = ' | '
    
    translator = googletrans.Translator()
    translated_text = translator.translate(total_screen_text).text

    vision_data = {"facial presence":facial_presence/(frame_number/5), 
                   "color": avg_rgb, 
                   "brightness": avg_bright, 
                   "screen_text": total_screen_text, 
                   "translated_text": translated_text,
                   "duration": video_time}

    return vision_data

print(scan_video_content(4))