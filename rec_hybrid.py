# basic library
import numpy as np 
import pandas as pd 

def create_new_user_rating(extracted_user_df, list_anime_id_rated, anime_df):
    dummy_user_id = 17000

    list_user_id = []
    list_score = []
    list_anime_id = []

    for i, row in anime_df.iterrows():
        list_user_id.append(dummy_user_id)
        list_score.append(0.742121)
        list_anime_id.append(row.anime_id)

    list_tuples = list(zip(list_user_id, list_score, list_anime_id)) 
    rating_dummy = pd.DataFrame(list_tuples, columns=['user_id', 'user_score', 'anime_id']) 

    rating_dummy = rating_dummy[~rating_dummy['anime_id'].isin(list_anime_id_rated)]

    list_user_id_rated = []
    list_score_rated = []
    list_anime_id_rated = []

    for i, row in extracted_user_df.iterrows():
        list_user_id_rated.append(dummy_user_id)
        list_score_rated.append(float(row.user_score)/10)
        list_anime_id_rated.append(row.anime_id)    

    list_tuples_rated = list(zip(list_user_id_rated, list_score_rated, list_anime_id_rated)) 
    rating_rated = pd.DataFrame(list_tuples_rated, columns=['user_id', 'user_score', 'anime_id']) 

    frames = [rating_dummy, rating_rated]
    result = pd.concat(frames)

    result = result[~result['anime_id'].isin(list_anime_id_rated)]

    merge_df = pd.merge(result, anime_df, how='left')

    merge_df = merge_df[merge_df['score'] > 0.1]

    return merge_df

def get_rec_hybrid(extracted_user_df, list_anime_id_rated, anime_df, model):
    one_user_df = create_new_user_rating(extracted_user_df, list_anime_id_rated, anime_df)

    user_id_test = one_user_df.user_id
    anime_id_test = one_user_df.anime_id
    anime_content_test = one_user_df.drop(['user_id', 'user_score', 'anime_id'], axis=1)
    
    predictions = model.predict([user_id_test, anime_id_test, anime_content_test])

    test_arr = predictions.ravel()
    pred_arr = pd.DataFrame(test_arr, columns = ['pred'])   
    
    dat1 = pred_arr.reset_index(drop=True)
    rec_idx = dat1.sort_values(by = ['pred'], ascending = False).index[1:11]
    rec = []
    for idx in rec_idx:
        rec.append(int(one_user_df.iloc[idx]['anime_id']))
    print(rec)
    return rec