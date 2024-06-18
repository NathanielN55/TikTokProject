import pandas as pd

def time_to_secs(duration):

    mins = int(duration[3]) * 60
    secs = (int(duration[5]) * 10) + int(duration[6])
    total = mins + secs

    return total

def new_row_from(df, ind):

    color_str = str(df['color_dominance'][ind])
    color_str = color_str.replace('(', "")
    color_str = color_str.replace(')', "")
    color = tuple(map(int, color_str.split(', ')))

    language = df['language'][ind]
    influencer_name = df['influencer_name'][ind]
    duration = time_to_secs(df['duration'][ind])
    red_dominance = color[0]
    green_dominance = color[1]
    blue_dominance = color[2]
    facial_presence = df['facial_presence'][ind]

    new_row = {'influencer_name': influencer_name, 'language': language, 'duration': duration, 
               'red_dominance': red_dominance, 'green_dominance': green_dominance, 'blue_dominance': blue_dominance, 
               'facial_presence': facial_presence}

    return new_row

video_data = pd.read_csv('output_data/tiktok_data3.csv')
video_data = video_data[["influencer_name", "vid_ID", "language", "date", "caption", 
                "caption_translated", "audio_original", "audio_translated", "screen_text", 
                "text_translated", "duration", "color_dominance", "facial_presence", "video_link"]]
video_data = video_data.drop_duplicates(subset=['vid_ID'])
print(video_data)

#print(video_data['duration'])

data_processed = pd.DataFrame(columns=['influencer_name', 'language', 'duration', 'red_dominance',
               'green_dominance', 'blue_dominance', 'facial_presence'])

for row in video_data.index:
    new_row = new_row_from(video_data, row)
    data_processed.loc[len(data_processed)] = new_row
    
print(data_processed)
    

grouped_mean = data_processed.groupby(['influencer_name','language']).mean().sort_values(by=['language'])
grouped_max = data_processed.groupby(['influencer_name','language']).max().sort_values(by=['language'])
grouped_min = data_processed.groupby(['influencer_name','language']).min().sort_values(by=['language'])

print('Mean: ')
print(grouped_mean)
print('Max: ')
print(grouped_max)
print('Min: ')
print(grouped_min)

