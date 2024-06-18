# Video and audio handling dependencies
import moviepy.editor
import speech_recognition as sr
import datetime

# Translation dependencies
import googletrans
from googletrans import *

# Computer vision dependencies
import cv2
import pathlib
import numpy as np
import easyocr
import math

# Dataframe handling dependencies
import pandas as pd

# File handling dependencies
import os


# Function to convert video audio to text
def vid_audio_to_text(id, language="english"):

    if language == "portuguese":
        language = "pt-BR"
    elif language == "arabic":
        language = "ar-EG"
    else:
        language = "en-US"

    # Open the video file with moviepy
    video = moviepy.editor.VideoFileClip(f'videos/{id}.mp4')

    print(f"Extracting audio from video {id}...")
    # Extract the audio from the video as a .wav file
    video.audio.write_audiofile(f'audio/{id}.wav')


    # Create an instance of a speech recognizer class
    r = sr.Recognizer()

    # Record the audio file so that the speech recognizer can process it
    with sr.AudioFile(f'audio/{id}.wav') as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.record(source)

    print(f"Extracting text from audio {id}...")
    text = "no text"
    try: 
        text = r.recognize_google(audio, language=language)
    except Exception as e:
        print(e)

    # print(text + '\n')
    return text


def scan_video_content(id, language='english'):

    if language == "arabic":
        reader = easyocr.Reader(['ar','en'])
    elif language == "portuguese":
        reader = easyocr.Reader(['pt', 'en'])
    else:
        reader = easyocr.Reader(['en'])

    # Get the path to the xml file that holds the info for the face detection training (included in OpenCV)
    cascade_path = pathlib.Path(cv2.__file__).parent.absolute() / "data/haarcascade_frontalface_default.xml"
    # Construct the face detection classifier with the accessed xml file
    clf = cv2.CascadeClassifier(str(cascade_path))
    # Open a video file with OpenCV
    video = cv2.VideoCapture(f"videos/{id}.mp4")

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
                scaleFactor=1.25,
                minNeighbors=6,
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            #facial_presence += len(faces)
            if (len(faces) > 0):
                facial_presence += 1
                

            # Dominant color detection
            height, width, _ = np.shape(frame)

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


            # current_frame_text = pytesseract.image_to_string(gray, lang='ara+eng')
            
            
            screen_text = reader.readtext(gray)
            current_frame_text = ''
            for i in screen_text:
                current_frame_text = current_frame_text + i[1] + '   '
                print(i[1])
            
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
            element = '   '
    
    translator = googletrans.Translator()
    translated_text = translator.translate(total_screen_text).text

    
    vision_data = {"facial_presence":facial_presence/(frame_number/5), 
                   "color": avg_rgb, 
                   "brightness": avg_bright, 
                   "screen_text": total_screen_text, 
                   "translated_text": translated_text,
                   "duration": video_time}

    return vision_data

# Function to scrape and store video page data
def scrape_all_video_data(id, language="english"):

    translator = googletrans.Translator()

    # Access data to put into the dataframe
    username = 0
    caption = 0
    date = 0
    audio_original = vid_audio_to_text(id, language)
    audio_translated = translator.translate(audio_original).text
    # print(audio_translated)

    video_content = scan_video_content(id, language)
    duration = video_content['duration']
    screen_text = video_content['screen_text']
    text_translated = video_content['translated_text']
    color_dominance = video_content['color']
    facial_presence = video_content['facial_presence']
    link = 0

    new_row = {"influencer_name":username, "vid_ID":0, "language":language, "date":date, "caption":caption, 
               "caption_translated":0, "audio_original": audio_original, "audio_translated": audio_translated, 
               "screen_text": screen_text, "text_translated": text_translated, "duration": duration, 
               "color_dominance": color_dominance, "facial_presence": facial_presence, "video_link":link}
    print(new_row)
    return new_row
    


def separate_filename(filename):
    id = ''
    username = filename
    for letter in filename:
        id = id + letter
        username = username[1:]
        if letter == '_':
            break
    
    id = id.replace('_', '')
    return [id, username]




# MAIN CODE:
    
tiktok_data = pd.DataFrame(columns = ["influencer_name", "vid_ID", "language", "date", "caption", 
                                      "caption_translated", "audio_original", "audio_translated", "screen_text", 
                                      "text_translated", "duration", "color_dominance", "facial_presence", "video_link"])

videos_titles = pd.read_csv("output_data/videos_titles.csv")
videos_titles = videos_titles[['vid_ID','influencer_name','video_url','title','language']]
print(videos_titles)
users_list = pd.read_csv("input_data/users_list.csv")

translator = googletrans.Translator()

# Iterate over rows in videos_titles
for ind in videos_titles.index:
    username = videos_titles['influencer_name'][ind]
    language = videos_titles['language'][ind]
    caption = videos_titles['title'][ind]
    id = str(videos_titles['vid_ID'][ind]) + '_' + str(username)

    # Collect the data for the new row
    
    if os.path.exists(f'videos/{id}.mp4'):   
        new_row = scrape_all_video_data(id, language)
        new_row["influencer_name"] = username
        new_row["language"] = language
        new_row["caption"] = caption
        new_row["caption_translated"] = translator.translate(caption).text
        new_row['text_translated'] = translator.translate(new_row['screen_text'])
        new_row["vid_ID"] = videos_titles['vid_ID'][ind]
        new_row["video_link"] = videos_titles['video_url'][ind]
        # Add the new row to the dataframe
        tiktok_data.loc[len(tiktok_data)] = new_row
        # Output to csv file
        tiktok_data.to_csv("output_data/tiktok_data.csv")

# # Get a list of the video files
# files = os.listdir('videos')
# print(files)

# # Iterate over video files in the videos directory
# for filename in files:
#     id = filename.replace(".mp4", "")
#     print(id)

#     # Extract username from filename
#     sep_name = separate_filename(id)
#     username = sep_name[1]
#     id_num = sep_name[0]

    
#     url = videos_titles['video_url'][int(id_num)]
#     user_ind = user_language = (users_list.loc[users_list['influencer_name'] == username])['language']
#     print(user_ind)
#     language = users_list['language'][user_ind]
#     print(language)

#     # Collect the data for the new row
#     new_row = scrape_all_video_data(url, id, language)
#     new_row["influencer_name"] = username
#     # Add the new row to the 
#     tiktok_data.loc[len(tiktok_data)] = new_row
#     # Output to csv file
#     tiktok_data.to_csv("output_data/tiktok_data.csv")

