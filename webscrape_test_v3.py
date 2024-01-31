from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen
import pandas as pd
import moviepy.editor
import speech_recognition as sr



# Function to get a list of videos from a particular user 
# when passing in the url to that particular user's page
def get_user_videos(driver, url):
    # Open the specified url
    driver.get(url)
    # Allow enough time to move past any sign-in page
    time.sleep(10)


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
def vid_audio_to_text(id):

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
        text = r.recognize_google(audio)
    except Exception as e:
        print(e)

    print(text + '\n')
    return text



# Function to scrape and store video page data
def scrape_video_data(driver, url, id, df):

    page_request = requests.get(url)

    # Download the video
    download_video(driver, url, id)

    # Open video page as html
    video_page = BeautifulSoup(page_request.content, "html.parser")
    # print(video_page.prettify())

    # Access data to put into the dataframe
    link = url
    username = video_page.find('span', {'data-e2e':'browse-username'})
    user_id = video_page.find('span', class_='css-1c7urt-SpanUniqueId')
    caption = 0
    video_text = vid_audio_to_text(id)
    date = 0

    new_row = {"username":username, "user_id":user_id, "caption":caption, "video_text":video_text, "date":date, "link":link}
    #print(new_row)
    df.loc[len(df)] = new_row



# MAIN CODE

# Open the Chrome browser
driver = webdriver.Chrome()

# Create a pandas dataframe to store data
data_columns = ["username", "user_id", "caption", "video_text", "date", "link"]
df = pd.DataFrame(columns=data_columns)

# Get a list of the videos from the user whose videos we are scraping
# Note: this url is currently just a placeholder; will figure out a way to read in 
# a list of urls or usernames later
videos = get_user_videos(driver, "https://www.tiktok.com/@dr.kojosarfo")



# For each video in the list of links, get video data
for video in videos:
    scrape_video_data(driver, video.a["href"], videos.index(video), df)

print(df)
df.to_csv("output_data/tiktok_data.csv")
