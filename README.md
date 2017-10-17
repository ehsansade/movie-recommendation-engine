# movie-recommendation-engine
The objective is to generate a list of movie recommendations based on a person's movies of interest and their contents.

I used complete set of MovieLens data, which included all movies until 2017.

The first step is to read the movie data as dataframes, and extract the year from the titles.

In the next step, I converted the rating values from [0,0.5,1,..,4.5,5] to [0,1], where the ratings higher than 3 gets value of 1 and the rest gets 0. The aim is to emphasize on positive ratings.

Now is time for building my recommendation engine. The engine gets 3 movie title from a person and find 10 best movie matches based on user-based collaboration and content-based filterings. It should be noted that some movie titles in the database have been written in a different format and they are required to be checked before running the recommendation engine.

The next steps for generating recommendation are:

1- Find users that like all 3 movies
2- Find all the movies that these similar users watched and rated
3- Aggreagte movies based on number of ratings and mean value of ratings, and genrate a movie list
4- Select a portion of the generated movie list based on  0.35* max(number of ratings)< number of ratings < max(number of ratings)

5- 
