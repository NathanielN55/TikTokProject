# Translation dependencies
import googletrans
from googletrans import *
from deep_translator import GoogleTranslator
import translators as ts

import time

# Data handling dependencies
import pandas as pd

def translate_text(text, lang):
    if lang == 'english':
        return text
    
    text_block = ''
    text_blocks_list = []
    translated = ''
    final_text = ''

    #translator = googletrans.Translator()

    for cha in text:
        text_block = text_block + (cha * 1)
        if len(text_block) == 4999:
            text_blocks_list.append(text_block)
            text_block = ''
    text_blocks_list.append(text_block)
    text_block = ''

    for block in text_blocks_list:
        # translated = GoogleTranslator(source='auto', target='en').translate(block)
        translated = ts.translate_text(block, translator="google", from_language="auto",to_language="en")
        time.sleep(1)
        final_text = final_text + translated
        
    return final_text



vid_data = pd.read_csv('output_data/tiktok_data4.csv')

vid_data = vid_data[['influencer_name','vid_ID','language','date','caption','caption_translated','audio_original',
                     'audio_translated','screen_text','text_translated','duration','color_dominance','facial_presence',
                     'video_link']]

caption_translated = ''
audio_translated = ''
text_translated = ''

for ind in vid_data.index:
    if ind > 174:
        caption_translated = translate_text(str(vid_data['caption'][ind]), str(vid_data['language'][ind]))
        vid_data['caption_translated'][ind] = caption_translated
        audio_translated = translate_text(str(vid_data['audio_original'][ind]), str(vid_data['language'][ind]))
        vid_data['audio_translated'][ind] = audio_translated
        text_translated = translate_text(str(vid_data['screen_text'][ind]), str(vid_data['language'][ind]))
        vid_data['text_translated'][ind] = text_translated
        print(vid_data.loc[ind])
        vid_data.to_csv('output_data/tiktok_data4.csv')