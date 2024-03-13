# Webscraping dependencies
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen

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
from pytesseract import pytesseract
import math

# Dataframe handling dependencies
import pandas as pd



# Function to get a list of videos from a particular user 
# when passing in the url to that particular user's page
def get_user_videos(driver, url):
    # Open the specified url
    driver.get(url)
    # Allow enough time to move past any sign-in page
    time.sleep(20)


    # Scroll through page
    # Temporarily commented out to limit number of videos to run through
    ''' 
    scroll_pause_time = 0.25
    screen_height = driver.execute_script("return window.screen.height;")
    i = 1

    while True:
        driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
        i += 1
        time.sleep(scroll_pause_time)
        scroll_height = driver.execute_script("return document.body.scrollHeight;")  
        if (screen_height) * i > scroll_height:
            time.sleep(20)
            if (screen_height) * i > scroll_height:
                break 
    '''
    
    page = BeautifulSoup(driver.page_source, "html.parser")

    # Find all html tags that contain video links
    videos = page.find_all("div", {"class": "css-x6y88p-DivItemContainerV2"})


    # Print number of videos and all the links to videos
    for video in videos:
        print(video.a["href"])
    print(len(videos))
    
    return videos



# Function to download a video from a video link
def download_video(driver, url, id):
    # Switch the web driver page to the tiktok downloader
    driver.get('https://ssstik.io/en')

    # Access the text bar to put the download link
    link_input_bar = driver.find_element(By.ID, 'main_page_text')
    # Put the link into the downloader website
    link_input_bar.send_keys(url)

    download_button = download_button = driver.find_element(By.ID, 'submit')
    download_button.click()
    time.sleep(8)

    # Access download button (basic download, not HD)
    download_button = driver.find_element(By.LINK_TEXT, 'Without watermark')
    # Get the download link from the button
    download_link = download_button.get_attribute('href')

    # Send a GET request to the download link with streaming enabled
    #response = requests.get(download_link, stream=True)
    #response.raise_for_status() # Raise an HTTP error for bad responses

    # Open a file to save the video content
    print(f"Downloading video_{id}...")
    mp4file = urlopen(download_link)
    with open(f"videos/video_{id}.mp4", "wb") as output:
        while True:
            data = mp4file.read(4096)
            if data:
                output.write(data)
            else:
                break
    


# Function to convert video audio to text
def vid_audio_to_text(id, language="en-US"):

    # Open the video file with moviepy
    video = moviepy.editor.VideoFileClip(f'videos/video_{id}.mp4')

    print(f"Extracting audio from video_{id}...")
    # Extract the audio from the video as a .wav file
    video.audio.write_audiofile(f'audio/audio_{id}.wav')


    # Create an instance of a speech recognizer class
    r = sr.Recognizer()

    # Record the audio file so that the speech recognizer can process it
    with sr.AudioFile(f'audio/audio_{id}.wav') as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.record(source)

    print(f"Extracting text from audio_{id}...")
    text = "no text"
    try: 
        text = r.recognize_google(audio, language=language)
    except Exception as e:
        print(e)

    # print(text + '\n')
    return text


def scan_video_content(id):

    reader = easyocr.Reader(['ar','en'])

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


            current_frame_text = pytesseract.image_to_string(gray, lang='ara+eng')
            
            # screen_text = reader.readtext(gray)
            # current_frame_text = ''
            # for i in screen_text:
            #     current_frame_text = current_frame_text + i[1] + ' | '
                #print(i[1])
            
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



# Function to scrape and store video page data
def scrape_all_video_data(url, id, df, language="en-US"):

    translator = googletrans.Translator()
    page_request = requests.get(url)

    # Download the video
    # download_video(driver, url, id)

    # Open video page as html
    video_page = BeautifulSoup(page_request.content, "html.parser")
    # print(video_page.prettify())

    # Access data to put into the dataframe
    username = video_page.find('span', {'data-e2e':'browse-username'})
    user_id = video_page.find('span', class_='css-1c7urt-SpanUniqueId')
    caption = 0
    date = 0
    audio_original = vid_audio_to_text(id, language)
    audio_translated = translator.translate(audio_original).text
    # print(audio_translated)

    video_content = scan_video_content(id)
    duration = video_content['duration']
    screen_text = video_content['screen_text']
    text_translated = video_content['translated_text']
    color_dominance = video_content['color']
    facial_presence = video_content['facial_presence']
    link = url

    new_row = {"username":username, "user_id":user_id, "caption":caption, "date":date, "audio_original": audio_original, 
               "audio_translated": audio_translated, "screen_text": screen_text, 
               "text_translated": text_translated, "duration": duration, 
               "color_dominance": color_dominance, "facial_presence": facial_presence, "video_link":link}
    print(new_row)
    df.loc[len(df)] = new_row



# MAIN CODE

url = "https://www.tiktok.com/@wjdanegypt"
# language = "en-US"
language = "ar-EG"
# language = "pt-BR"

# Open the Chrome browser
driver = webdriver.Chrome()

# Create a pandas dataframe to store data
data_columns = ["username", "user_id", "caption", "date", "audio_original", "audio_translated",
               "screen_text", "text_translated", "duration", "color_dominance", "facial_presence", 
               "video_link"]
df = pd.DataFrame(columns=data_columns)

# Get a list of the videos from the user whose videos we are scraping
# Note: this url is currently just a placeholder; will figure out a way to read in 
# a list of urls or usernames later
videos = get_user_videos(driver, url)



# For each video in the list of links, download the video
for video in videos:
    # Make sure it is a video link before downloading, rather than a photo link
    # Otherwise the current download text will not work
    if video.a["href"][-25:-20] == "video":
        download_video(driver, video.a["href"], videos.index(video))
        scrape_all_video_data(driver, video.a["href"], videos.index(video), df, language=language)
        df.to_csv("output_data/tiktok_data.csv")


driver.quit()
for video in videos:
    # Make sure it is a video link before downloading, rather than a photo link
    # Otherwise the current download text will not work
    if video.a["href"][-25:-20] == "video":
        scrape_all_video_data(video.a["href"], videos.index(video), df, language=language)
        df.to_csv("output_data/tiktok_data.csv")

print(df)
df.to_csv("output_data/tiktok_data.csv")