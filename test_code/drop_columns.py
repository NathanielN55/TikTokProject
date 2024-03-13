import pandas as pd

df = pd.read_csv("output_data/tiktok_data.csv")
print(df)
new_df = df.drop(columns=["Unnamed: 0", "username", "user_id", "caption", "date","on_screen_text", "duration", "color_dominance", "facial_presence", "entropy"])
print(new_df)
new_df.to_csv("output_data/datasample_arbc.csv")