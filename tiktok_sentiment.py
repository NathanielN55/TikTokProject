import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

video_data = pd.read_csv('output_data/tiktok_data4.csv')

sentiment_data = pd.read_csv('output_data/data_complete.csv')
sentiment_data = sentiment_data[['influencer_name','vid_ID','language','caption','caption_translated', 'caption_sentiment',
                                       'audio_original', 'audio_translated', 'audio_sentiment', 'screen_text',
                                       'text_translated', 'text_sentiment', 'duration', 'color_dominance','facial_presence', 'video_link']]

vader = SentimentIntensityAnalyzer()

for ind in video_data.index:
    if ind > 224:
        influencer_name = video_data['influencer_name'][ind]
        vid_ID = video_data['vid_ID'][ind]
        language = video_data['language'][ind]
        caption = video_data['caption'][ind]
        caption_translated = video_data['caption_translated'][ind]

        caption_sentiment = vader.polarity_scores(str(video_data['caption_translated'][ind]))['compound']

        audio_original = video_data['audio_original'][ind]
        audio_translated = video_data['audio_translated'][ind]

        audio_sentiment = 0
        if audio_sentiment != '':
            audio_sentiment = vader.polarity_scores(str(video_data['audio_translated'][ind]))['compound']

        screen_text = video_data['screen_text'][ind]
        text_translated = video_data['text_translated'][ind]

        text_sentiment = 0
        if text_sentiment != '':
            text_sentiment = vader.polarity_scores(str(video_data['text_translated'][ind]))['compound']

        duration = video_data['duration'][ind]
        color_dominance = video_data['color_dominance'][ind]
        facial_presence = video_data['facial_presence'][ind]
        video_link = video_data['video_link'][ind]

        new_row = {'influencer_name': influencer_name,'vid_ID': vid_ID,'language': language,'caption': caption,
                'caption_translated': caption_translated, 'caption_sentiment': caption_sentiment,
                    'audio_original': audio_original, 'audio_translated': audio_translated, 'audio_sentiment': audio_sentiment,
                    'screen_text': screen_text, 'text_translated': text_translated, 'text_sentiment': text_sentiment, 
                    'duration': duration, 'color_dominance': color_dominance,'facial_presence': facial_presence, 
                    'video_link': video_link}
        
        print(new_row['influencer_name'] + ' ' + new_row['language'] + ', ' + str(new_row['caption_sentiment']) + 
              ", " + str(new_row['audio_sentiment']) 
              + ", " + str(new_row['text_sentiment']))
        #sentiment_data.loc[len(sentiment_data)] = new_row
        #print(sentiment_data[['influencer_name', 'vid_ID', 'caption_sentiment', 'audio_sentiment', 'text_sentiment']])
        #sentiment_data.to_csv('output_data/data_complete.csv')