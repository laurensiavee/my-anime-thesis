# basic library
import numpy as np 
import pandas as pd 

def get_rec_collaborative_anime(anime_id, item_sim_df):
    rec = item_sim_df.sort_values(by = anime_id, ascending = False).index[1:11]
    return rec

def get_rec_collaborative_user(anime_id, user_sim_df):
    rec = user_sim_df.sort_values(by = int(anime_id), ascending = False).index[1:11]
    return rec

