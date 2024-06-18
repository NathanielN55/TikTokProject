# Webscraping dependencies
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen

# Dataframe handling dependencies
import pandas as pd


def get_video_name(driver, url):
    driver.get(url)
    #time.sleep(6)

    # Find all html tags that contain video links
    try:
         title_container = driver.find_element(By.TAG_NAME, 'h1')
    except BaseException:
         return 'no title found'

    video_name = title_container.text
    video_name = video_name.replace("\n", " ")

    return video_name


# Open the Chrome browser
driver = webdriver.Chrome()

# Open the video links data
videos_list = pd.read_csv("input_data/video_links.csv")
videos_list = videos_list[["influencer_name","video_url"]]
vids_titles_list = pd.read_csv("output_data/videos_titles.csv")
vids_titles_list = vids_titles_list[["influencer_name","video_url","title"]]

driver.get(videos_list["video_url"][0])
time.sleep(15)

# Run through each video in the videos list to extract the name of the video
for ind in videos_list.index:
    #print(vids_titles_list["title"][ind])
    if pd.isna(vids_titles_list.at[ind,'title']) or vids_titles_list['title'][ind] == "This site can't be reached" or vids_titles_list['title'][ind] == "no title found": #["title"][ind].isna:
        video_name = ''
        link = videos_list["video_url"][ind]
        if link[-25:-20] == "video":
            # Get the caption for the video
            video_name = get_video_name(driver, link)
            print(str(ind) + ": " + str(video_name))
            # Create a new row for the database
            # new_row = {"influencer_name":(videos_list["influencer_name"][ind]),
            #            "video_url":(videos_list["video_url"][ind]),"title":video_name}
            # # Add the new row to the dataframe with titles
            # vids_titles_list.loc[len(vids_titles_list)] = new_row
            vids_titles_list.at[ind, "title"] = video_name

            vids_titles_list.to_csv("output_data/videos_titles.csv")
            #time.sleep(1)
