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

ratings['year'] = ratings.title.str.split('(').str.get(-1) 
ratings['year'] = ratings.year.str.split(')').str.get(0)

ratings=ratings[['userId','movieId','rating','title','year']]
ratings['year'] = ratings['year'].astype(str)
ratings=ratings[ratings['year'].map(len)==4]
ratings=ratings[ratings['year']!='Viva']
ratings=ratings[ratings['year']!='Wall']
ratings=ratings[ratings['year']!='Mara']
ratings=ratings[ratings['year']!='Fant']
ratings=ratings[ratings['year']!='Zero']
ratings['year'] = ratings['year'].astype(int)
# if you want ot consider certain years, e.g. year>2000, you can filter and assign it to new_ratings
#new_ratings=ratings[ratings['year']>1995]
new_ratings=ratings

new_ratings['rating'] = np.where(new_ratings['rating'] > 3, 1, 0)
movie_list=new_ratings.groupby('movieId').head(1)

positive_ratings=new_ratings[new_ratings['rating']==1]
movie_list2=positive_ratings.groupby('movieId').head(1)

# list of 3 favorite movies and locating them in the database
print('Enter name of three favourite movie, seperated by comma')
movie_names=input()
print('Enter year of three favourite movie, seperated by comma')
movie_years=input()
movie_name_database=new_ratings.groupby('title').head(1)
movie_names=movie_names.split(',')
movie_years=movie_years.split(',')
a0=movie_name_database.loc[movie_name_database.title.str.contains(movie_names[0])]
a1=movie_name_database.loc[movie_name_database.title.str.contains(movie_names[1])]
a2=movie_name_database.loc[movie_name_database.title.str.contains(movie_names[2])]
a0=a0[a0.year==int(movie_years[0])]
a1=a1[a1.year==int(movie_years[1])]
a2=a2[a2.year==int(movie_years[2])]
movie_title=list(a0.title)+list(a1.title)+list(a2.title)
###
similar_users=positive_ratings[positive_ratings['title']==movie_title[0]]
similar_users1=positive_ratings[positive_ratings['userId'].isin(similar_users['userId'])]
similar_users=similar_users1[similar_users1['title']==movie_title[1]]
similar_users2=similar_users1[similar_users1['userId'].isin(similar_users['userId'])]
similar_users=similar_users2[similar_users2['title']==movie_title[2]]

similar_movies=new_ratings[new_ratings['userId'].isin(similar_users['userId'])]
recom_movies=similar_movies.groupby('title',as_index=False).agg({'rating': [np.size, np.mean]})

min_size= max(recom_movies[~recom_movies['title'].isin(movie_title)][('rating','size')])*0.3
recom_movies=recom_movies[(recom_movies[('rating','size')]>min_size) &(recom_movies[('rating','mean')]>.75)]

recom_movies=pd.merge(recom_movies,dg,on='title')

recom_movies['genre1'] = recom_movies.genres.str.split('|').str.get(0)
recom_movies['genre2'] = recom_movies.genres.str.split('|').str.get(1)

newdf = recom_movies[recom_movies.columns[[0,4,3,2,6,7]]].sort_values([('rating','size')], ascending=False)

dlink = pd.read_csv('C:/Users/ehsan/python work/ml-latest/links.csv', sep=',')

newdf=pd.merge(newdf,dlink)

# Similarity in directors and main casts
for i in range(len(recom_movies)):
    url='http://www.imdb.com/title/tt%s/' % newdf['imdbId'][i]+'fullcredits'

    page = requests.get(url)
    if page:
        list_tables = pd.read_html(page.content)
    else:
        url='http://www.imdb.com/title/tt0%s/' % newdf['imdbId'][i]+'fullcredits'
        page = requests.get(url)
        if page:
            
            list_tables = pd.read_html(page.content)
        else:
            break
    
    
    newdf.loc[i,'cast1']=list_tables[2][1][1]
    
    newdf.loc[i,'cast2']=list_tables[2][1][2]
    
    newdf.loc[i,'cast3']=list_tables[2][1][3]
    
    newdf.loc[i,'director']=list_tables[0][0][0]
    
    
    if len(list_tables[0][0])>1:
        
        newdf.loc[i,'director2']=list_tables[0][0][1]

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
   # the weighting for crew similarity can be changed here
    
new_list=new_list.reset_index(drop=True).sort_values([('rating','mean')], ascending=False)

recom_list=new_list.head(50).sort_values(['content_similarity',('rating','mean'),('rating','size')],ascending=[False,False,False]).head(10)
Print(recom_list)

