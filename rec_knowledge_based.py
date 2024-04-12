import numpy as np 
import pandas as pd 

def get_top_ranked(anime_subset, n):
    list_id = []

    temp = anime_subset.sort_values(by=['score'], ascending=False)
    temp.drop(temp[temp['score'] < 1].index, inplace=True)
    temp = temp.head(n)
    for i, row in temp.iterrows():
        list_id.append(row['anime_id'])

    return list_id

def get_top_popularity(anime_subset, n):
    list_id = []

    temp = anime_subset.sort_values(by=['popularity'], ascending=True)
    temp.drop(temp[temp['popularity'] < 1].index, inplace=True)
    temp = temp.head(n)
    for i, row in temp.iterrows():
        list_id.append(row['anime_id'])

    return list_id

def get_top_genre(anime_subset, n, genre):
    contain_values = anime_subset[anime_subset['genre'].str.contains("(?i)" + genre, na=False)]

    list_id = []

    temp = contain_values.sort_values(by=['score'], ascending=False)
    temp.drop(temp[temp['score'] < 1].index, inplace=True)
    temp = temp.head(n)
    for i, row in temp.iterrows():
        list_id.append(row['anime_id'])

    return list_id