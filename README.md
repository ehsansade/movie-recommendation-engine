# movie-recommendation-engine
The objective is to generate a list of movie recommendations based on a person's movies of interest and their contents.

I used complete set of MovieLens data, which included all movies until 2017.

The first step is to read the movie data as dataframes, and extract the year from the titles.

In the next step, I converted the rating values from [0,0.5,1,..,4.5,5] to [0,1], where the ratings higher than 3 gets value of 1 and the rest gets 0. The aim is to emphasize on positive ratings.

Now is time for building my recommendation engine. The engine gets 3 movie title from a person and find 10 best movie matches based on user-based collaboration and content-based filterings.
