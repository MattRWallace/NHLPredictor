# NHL Predictor
This project started with me wanting a project that would give me the opportunity to practice and really internalize the python syntax that I was learning and my discovery that the NHL has a publicly available API where I could obtain stats.

# Design
**Tech used**: Python, SQLite
The app is CLI only and there are 3 main commands that structure the behavior of the app: Build, Train and Predict. While there is more detailed documentation later in this document, I will briefly summarize them here.

## Build
This fetches all the raw data from the NHL API and stores it locally in an SQLite database using the SqliteDict package for interfacing with the database itself. The only thing this command does is downloading and updating the data in the database.

## Train
This is the step that actually builds a machine learning model.  There's two major components to be aware of: The ML algorithm implementation and what I'm calling the summarizer. Both of these components are consumed via dependency injection making the app adaptable. The summarizer is the product of a need to flatten all the player statistics into a smaller set of stats that pertain to a given game; it summarizes the individual stats for each player in a game into an overall roster score for that team in that game.  Similarly, when later trying to predict a future game outcome, we will want to summarize the past performance of each player listed on the game roster and use that when making our predictions. The summarizer is fully responsible for taking data persisted in the database and manipulating it into a data set appropriate for a ML algorithm to use.

## Predict
This is the last step and hopefully the one you will be using the most.  The data has been downloaded and stored in a local database.  You have run the Train step and you now have a persisted file with your trained model saved on your disk.  You're now ready to see what predictions your model can produce. This command also lets you query and list games that are on the schedule for today which makes it a little bit easier to specify which games you want predicted.

# Build
TODO

# Train
TODO

# Predict
TODO

# Adding support for other machine learning algorithms
TODO

# Adding new summarizers
As mentioned earlier, summarizers provide the logic to clean up and prepare the data for consumption by an ML algorithm.  For now there is only one summarizer implemented which performs a naive summation of most of the statistics for a particular game to get the overall roster strength. Depending on the need, a summarizer might be tied to a specific ML algorithm (e.g. if the algorithm has unique data needs, a custom summarizer is the place to do that).