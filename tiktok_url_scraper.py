# Webscraping dependencies
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen

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


# MAIN CODE

# Open the list of user urls as a pandas dataframe
users_list = pd.read_csv("input_data/users_list.csv")
# print(users_list)

# Open the Chrome browser
driver = webdriver.Chrome()

# Create a pandas dataframe to store data
data_columns = ["user", "video_url"]
videos_list = pd.read_csv("input_data/video_links.csv")
videos_list = videos_list[["influencer_name", "video_url"]]
print(videos_list)

# Get a list of the videos from the user whose videos we are scraping
for ind in users_list.index:

    link = users_list["url"][ind]
    username = users_list['influencer_name'][ind]
    # If the urls have not been gathered from this user yet, gather the urls
    if not(username in set(videos_list['influencer_name'])):
        print(link, username)
        videos = get_user_videos(driver, link)

        # Once the video urls are gathered from the user, add them to the video links list
        for video in videos:
            new_row = {"influencer_name": username, "video_url": video.a["href"]}
            videos_list.loc[len(videos_list)] = new_row
            videos_list.to_csv("input_data/video_links.csv")


print(videos_list)
videos_list.to_csv("input_data/video_links.csv")