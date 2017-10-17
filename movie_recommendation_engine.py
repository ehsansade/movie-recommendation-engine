# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 19:44:48 2017

@author: ehsan
"""

import pandas as pd
import numpy as np
from lxml import html
import requests

df = pd.read_csv('C:/Users/ehsan/python work/ml-latest/ratings.csv', sep=',')
dg = pd.read_csv('C:/Users/ehsan/python work/ml-latest/movies.csv', sep=',')

ratings=pd.merge(df,dg)

ratings['year'] = ratings.title.str.split('(').str.get(1) 
ratings['year'] = ratings.year.str.split(')').str.get(0)

ratings=ratings[['userId','movieId','rating','title','year']]
ratings['year'] = ratings['year'].astype(str)
ratings['year'] = ratings['year'].convert_objects(convert_numeric=True)

#new_ratings=ratings[ratings['year']>2004]
new_ratings=ratings
#new_ratings =new_ratings [new_ratings['rating'] != 3]

# Encode 4s and 5s as 1 (rated positively)
# Encode 1s and 2s as 0 (rated poorly)
new_ratings['rating'] = np.where(new_ratings['rating'] > 3, 1, 0)
movie_list=new_ratings.groupby('movieId').head(1)
#movie_list.to_csv('movie_list.csv', index=False, header=True)
positive_ratings=new_ratings[new_ratings['rating']==1]
movie_list2=positive_ratings.groupby('movieId').head(1)
#movie_list2.to_csv('movie_list2.csv', index=False, header=True)

movie_title=['Mr. Nobody (2009)','Truman Show, The (1998)','Gone with the Wind (1939)']
similar_users=positive_ratings[positive_ratings['title']==movie_title[0]]
similar_users1=positive_ratings[positive_ratings['userId'].isin(similar_users['userId'])]
similar_users=similar_users1[similar_users1['title']==movie_title[1]]
similar_users2=similar_users1[similar_users1['userId'].isin(similar_users['userId'])]
similar_users=similar_users2[similar_users2['title']==movie_title[2]]
#similar_users=similar_users2[similar_users2['userId'].isin(similar_users['userId'])]

similar_movies=new_ratings[new_ratings['userId'].isin(similar_users['userId'])]
#similar_movies=similar_movies[~similar_movies['title'].isin(movie_title)]
recom_movies=similar_movies.groupby('title',as_index=False).agg({'rating': [np.size, np.mean]})

min_size= max(recom_movies[~recom_movies['title'].isin(movie_title)][('rating','size')])*0.35
recom_movies=recom_movies[(recom_movies[('rating','size')]>min_size) &(recom_movies[('rating','mean')]>.8)]
#recom_movies['title']=recom_movies.index

recom_movies=pd.merge(recom_movies,dg,on='title')

recom_movies['genre1'] = recom_movies.genres.str.split('|').str.get(0)
recom_movies['genre2'] = recom_movies.genres.str.split('|').str.get(1)

newdf = recom_movies[recom_movies.columns[[0,4,3,2,6,7]]].sort_values([('rating','size')], ascending=False)

dlink = pd.read_csv('C:/Users/ehsan/python work/ml-latest/links.csv', sep=',')

newdf=pd.merge(newdf,dlink)

for i in range(len(recom_movies)):
    url='http://www.imdb.com/title/tt0%s/' % newdf['imdbId'][i]
    page = requests.get(url)
    tree = html.fromstring(page.content)
    cast = tree.xpath('//*[@id="title-overview-widget"]/div[3]/div[1]/div[4]/span/a/span/text()')
    if cast==[]:
        cast = tree.xpath('//*[@id="title-overview-widget"]/div[3]/div[2]/div[1]/div[4]/span/a/span/text()') 
    
    director = tree.xpath('//*[@id="title-overview-widget"]/div[3]/div[1]/div[2]/span/a/span/text()')
    if director==[]:
        director = tree.xpath('//*[@id="title-overview-widget"]/div[3]/div[2]/div[1]/div[2]/span/a/span/text()')
    if cast==[]:
        cast=tree.xpath('//*[@id="title-overview-widget"]/div[3]/div[2]/div[1]/div[2]/span/a/span/text()')
        director=[]
    #movie_list['director'][i]=director
    if len(cast)>0:
        newdf.loc[i,'cast1']=cast[0]
    if len(cast)>1:
        newdf.loc[i,'cast2']=cast[1]
    if len(cast)>2:
        newdf.loc[i,'cast3']=cast[2]
    if len(director)>0:
        newdf.loc[i,'director']=director[0]
    if len(director)>1:
        newdf.loc[i,'director2']=director[1]

new_list=newdf[~newdf['title'].isin(movie_title)]
new_list=new_list.reset_index(drop=True).sort_values([('rating','mean')], ascending=False)

favorite_movies=newdf[newdf['title'].isin(movie_title)].reset_index(drop=True)

casts=[]
for i in range(3):
    if isinstance(favorite_movies.loc[i,'cast1'], str):
        casts.append(favorite_movies.loc[i,'cast1'])
    if isinstance(favorite_movies.loc[i,'cast2'], str):
        casts.append(favorite_movies.loc[i,'cast2'])
    if isinstance(favorite_movies.loc[i,'cast3'], str):
        casts.append(favorite_movies.loc[i,'cast3'])

directors=[]
for i in range(3):
    if isinstance(favorite_movies.loc[i,'director'], str):
        directors.append(favorite_movies.loc[i,'director'])
    if isinstance(favorite_movies.loc[i,'director2'], str):
        directors.append(favorite_movies.loc[i,'director2'])
        
genres=[]
count=0
for i in range(3):
    if isinstance(favorite_movies.loc[i,'genre1'], str):
        if favorite_movies.loc[i,'genre1']=='Comedy':
            if count<2:
                genres.append(favorite_movies.loc[i,'genre1'])
                count=count+1
        else:
            genres.append(favorite_movies.loc[i,'genre1'])
            
    if isinstance(favorite_movies.loc[i,'genre2'], str):
        if favorite_movies.loc[i,'genre2']=='Comedy':
            if count<2:
                genres.append(favorite_movies.loc[i,'genre2'])
                count=count+1
        else:
            genres.append(favorite_movies.loc[i,'genre2'])

for i in range(len(new_list)):
    crew_similarity=0
    for item in casts:
        if new_list.loc[i,'cast1']==item:
            crew_similarity=crew_similarity+1
        if new_list.loc[i,'cast2']==item:
            crew_similarity=crew_similarity+1
        if new_list.loc[i,'cast3']==item:
            crew_similarity=crew_similarity+1
    
    for item in directors:
        if new_list.loc[i,'director']==item:
            crew_similarity=crew_similarity+1
        if new_list.loc[i,'director2']==item:
            crew_similarity=crew_similarity+1
    new_list.loc[i,'crew_similarity']=crew_similarity

    genre_similarity=0
    for item in genres:
        if new_list.loc[i,'genre1']==item:
            genre_similarity=genre_similarity+1
        if new_list.loc[i,'genre2']==item:
            genre_similarity=genre_similarity+1
    new_list.loc[i,'genre_similarity']=genre_similarity
    new_list.loc[i,'content_similarity']=genre_similarity+1.5*crew_similarity
    
new_list=new_list.reset_index(drop=True).sort_values([('rating','mean')], ascending=False)
    
list1=new_list.head(20).sort_values(['content_similarity',('rating','mean'),('rating','size')],ascending=[False,False,False]).head(10)
list2=new_list.head(30).sort_values(['content_similarity',('rating','mean'),('rating','size')],ascending=[False,False,False]).head(10)
list3=new_list.head(50).sort_values(['content_similarity',('rating','mean'),('rating','size')],ascending=[False,False,False]).head(10)
list4=new_list.head(100).sort_values(['content_similarity',('rating','mean'),('rating','size')],ascending=[False,False,False]).head(10)
# best recommenders list2, 3