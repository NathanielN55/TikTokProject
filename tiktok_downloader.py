# Webscraping dependencies
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen

# Dataframe handling dependencies
import pandas as pd



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
    time.sleep(10)


    # Access download button (basic download, not HD)
    try:
        download_button = driver.find_element(By.LINK_TEXT, 'Without watermark')
    except BaseException:
        # print("Could not download data")
        return
    
    # Get the download link from the button
    download_link = download_button.get_attribute('href')

    # Send a GET request to the download link with streaming enabled
    #response = requests.get(download_link, stream=True)
    #response.raise_for_status() # Raise an HTTP error for bad responses

    # Open a file to save the video content
    print(f"Downloading video {id}.mp4...")
    mp4file = urlopen(download_link)
    with open(f"videos/{id}.mp4", "wb") as output:
        while True:
            data = mp4file.read(4096)
            if data:
                output.write(data)
            else:
                break



# MAIN CODE

# Open the Chrome browser
driver = webdriver.Chrome()
# Open the video links data
videos_list = pd.read_csv("input_data/video_links.csv")
videos_list = videos_list[["influencer_name","video_url"]]
# Open the users list data
users_list = pd.read_csv("input_data/users_list.csv")
users_list = users_list[["influencer_name","number_of_followers","url","credential","language"]]


# For each video in the list of links, download the video
for ind in videos_list.index:
    # Change this number to specify which indeces to exclude (prevents unneccesary re-downloading)
    if ind > 1048:
        # Make sure it is a video link before downloading, rather than a photo link
        # Otherwise the current download text will not work
        link = videos_list["video_url"][ind]
        filename = str(ind) + "_" + str(videos_list["influencer_name"][ind]) 
        if link[-25:-20] == "video":
            download_video(driver, link, filename)
            time.sleep(1)