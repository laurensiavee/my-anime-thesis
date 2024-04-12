import numpy as np 
import pandas as pd 

"""
anime_id,
title,
score,
rating_count,
ranked,
popularity,
members,
type,
studio,
synopsis,
episode_count,
genre,
url,
img
"""

####################
# GET SINGLE FEATURES
####################
def get_anime_title(anime_subset, anime_id):
    id = int(str(anime_id))
    df_filter = anime_subset[anime_subset['anime_id'] == id]
    row = df_filter.iloc[0]
    result = row['title']
    return result

def get_anime_score(anime_subset, anime_id):
    id = int(str(anime_id))
    df_filter = anime_subset[anime_subset['anime_id'] == id]
    row = df_filter.iloc[0]
    result = row['score']
    return result

def get_anime_type(anime_subset, anime_id):
    id = int(str(anime_id))
    df_filter = anime_subset[anime_subset['anime_id'] == id]
    row = df_filter.iloc[0]
    result = row['type']
    return result

def get_anime_ep_count(anime_subset, anime_id):
    id = int(str(anime_id))
    df_filter = anime_subset[anime_subset['anime_id'] == id]
    row = df_filter.iloc[0]
    result = row['episode_count']
    return result

def get_anime_genre(anime_subset, anime_id):
    id = int(str(anime_id))
    df_filter = anime_subset[anime_subset['anime_id'] == id]
    row = df_filter.iloc[0]
    result = row['genre']
    return result

def get_anime_img_url(anime_subset, anime_id):
    id = int(str(anime_id))
    df_filter = anime_subset[anime_subset['anime_id'] == id]
    row = df_filter.iloc[0]
    result = row['img']
    return result

def get_anime_ranked(anime_subset, anime_id):
    id = int(str(anime_id))
    df_filter = anime_subset[anime_subset['anime_id'] == id]
    row = df_filter.iloc[0]
    result = row['ranked']
    return result

def get_anime_rating_count(anime_subset, anime_id):
    id = int(str(anime_id))
    df_filter = anime_subset[anime_subset['anime_id'] == id]
    row = df_filter.iloc[0]
    result = row['rating_count']
    return result

def get_anime_popularity(anime_subset, anime_id):
    id = int(str(anime_id))
    df_filter = anime_subset[anime_subset['anime_id'] == id]
    row = df_filter.iloc[0]
    result = row['popularity']
    return result

def get_anime_members(anime_subset, anime_id):
    id = int(str(anime_id))
    df_filter = anime_subset[anime_subset['anime_id'] == id]
    row = df_filter.iloc[0]
    result = row['members']
    return result
    
def get_anime_studio(anime_subset, anime_id):
    id = int(str(anime_id))
    df_filter = anime_subset[anime_subset['anime_id'] == id]
    row = df_filter.iloc[0]
    result = row['studio']
    return result

def get_anime_mal_url(anime_subset, anime_id):
    id = int(str(anime_id))
    df_filter = anime_subset[anime_subset['anime_id'] == id]
    row = df_filter.iloc[0]
    result = row['url']
    return result

def get_anime_synopsis(anime_subset, anime_id):
    id = int(str(anime_id))
    df_filter = anime_subset[anime_subset['anime_id'] == id]
    row = df_filter.iloc[0]
    result = row['synopsis']
    return result

####################
# GET PROPERTIES FOR CARD
####################

def get_card_s_prop(anime_subset, anime_id):
    title = get_anime_title(anime_subset, anime_id)
    type = get_anime_type(anime_subset, anime_id)
    ep_count = int(get_anime_ep_count(anime_subset, anime_id))
    genre = get_anime_genre(anime_subset, anime_id)
    img_url = get_anime_img_url(anime_subset, anime_id)
    score = "{:.2f}".format(get_anime_score(anime_subset, anime_id))
    return [title, type, ep_count, genre, img_url, score]

def get_complete_anime_details(anime_subset, anime_id):
    title = get_anime_title(anime_subset, anime_id)
    type = get_anime_type(anime_subset, anime_id)
    ep_count = int(get_anime_ep_count(anime_subset, anime_id))
    genre = get_anime_genre(anime_subset, anime_id)
    img_url = get_anime_img_url(anime_subset, anime_id)
    score = "{:.2f}".format(get_anime_score(anime_subset, anime_id))
    ranked = int(get_anime_ranked(anime_subset, anime_id))
    rating_count = int(get_anime_rating_count(anime_subset, anime_id))
    popularity = int(get_anime_popularity(anime_subset, anime_id))
    members = int(get_anime_members(anime_subset, anime_id))
    studio = get_anime_studio(anime_subset, anime_id)
    mal_url = get_anime_mal_url(anime_subset, anime_id)
    synopsis = get_anime_synopsis(anime_subset, anime_id)

    return [title, type, ep_count, genre, img_url, score, 
    ranked, rating_count, popularity, members, studio, mal_url, synopsis]
