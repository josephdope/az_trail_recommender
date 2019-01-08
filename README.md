# Take A Hike - Arizona
### Project Goal:
As an outdoor enthusiast, I frequently find myself on the same trails over and over again. I wanted to create an easy way to discover new trails. There were two major components to this project, building a recommendation system when facing the “cold start” problem as well as a model that exploits user rating trends in order to recommend trails.

The cold start problem comes about when a user has little to no previous rating history. In order to recommend a trail in this scenario, a common practice is to use a content-based method, which finds the similarities between trails based on the features of the trails. These features included items such distance, elevation gain, rating, location, tags, and the description of the trails.

User ratings can be utilized to build a collaborative filtering model that essentially finds the trends of observed ratings to predict unknown ratings for trails. While this does require an active user-base, it allows for a much more natural recommendation system based on what similar users like.

<img src="https://i0.wp.com/datameetsmedia.com/wp-content/uploads/2018/05/2ebah6c.png?resize=1024%2C627" >

### Data:
Data was gathered from AllTrails.com via web-scraping and stored in a PostgreSQL database.

### Results and Findings:
The biggest challenge for this project was gathering the data. Web-scraping can be a fickle thing. It took hours to scrape the necessary data from the webpages of more than 1400 trails. In order to grab all of the reviews, an action had to be created to load more reviews, 30 at a time. It was a painstaking process. I frequently ran into errors and had to restart multiple times.

Of course, when the data was finally gathered and exported to a SQL database, some manipulation had to be done. Kilometers had to be converted to miles, meters converted to feet, and text had to be represented numerically.

###### Models Used:

•	Content-Based: cosine distance was used to calculate the similarity between trails. A matrix of distances was created. For the trail input by the user, the top 10 most similar are shown.

•	Collaborative Filtering: an SVD model from scikit learn was utilized to predict user ratings on trails they have not yet rated. The top 10 highest anticipated ratings are shown.

### Technologies Used:
<img src="https://github.com/josephdope/az_trail_recommender/blob/master/Technologies_used.png" >
