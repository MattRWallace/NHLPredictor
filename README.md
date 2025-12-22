# NHL Predictor
This project started with a combination of me wanting a project that would give me the opportunity to practice and really internalize the python syntax that I was learning and my discovery that the NHL has a publicly available API where I could obtain stats. I decided that I wanted to try and use some of the ML knowledge I picked up in college to see if I could successfully predict the outcomes of NHL hockey games.

## Install
`pip install NHL-predictor`

## Usage
This is a CLI only app implemented using [Typer](https://typer.tiangolo.com/). As such, you can see the usage at any time with the `--help` argument.

![nhlpredictor --help](https://raw.githubusercontent.com/MattRWallace/NHLPredictor/refs/heads/screenshots/screenshots/nhlpredictor.png)

The app flow should progress from build -> train -> predict. For example, you might run the following commands:

```
$ nhlpredictor build --all-seasons
$ nhlpredictor train --algorithm linearregression --output Average_LinearRegressionModel.pkl --summarizer-type average
$ nhlpredictor predict --algorithm linearregression --summarizer-type average --model Average_LinearRegressionModel.pkl
```

After running the train operation you will find statistics about the model displayed in the console.  It should look something like this:

```
Stats from train operation:
┌───────────────────────┬──────────────────────┐
│  R-squared            │  0.7542777015007675  │
│  Mean squared error:  │  0.24                │
└───────────────────────┴──────────────────────┘
PValues:
┌────────────────────────────────────────┬──────────────────────────┐
│  const                                 │  9.405692100270518e-01   │
│  skater_goals_home                     │  9.186727854315457e-25   │
│  skater_assists_home                   │  6.844242313622373e-24   │
...
│  goalie_shorthandedSavesAgainst_away   │  4.8229048152259835e-01  │
│  goalie_saveSavesAgainst_away          │  9.045808182232136e-01   │
└────────────────────────────────────────┴──────────────────────────┘
Stats from test operation:
┌───────────────────────┬──────────────────────┐
│  R-squared:           │  0.7626640893213292  │
│  Mean squared error:  │  0.24                │
└───────────────────────┴──────────────────────┘
PValues:
┌────────────────────────────────────────┬──────────────────────────┐
│  const                                 │  5.053272997277648e-01   │
│  skater_goals_home                     │  2.475192098045989e-10   │
│  skater_assists_home                   │  1.8078109513387622e-10  │
...
│  goalie_shorthandedSavesAgainst_away   │  6.267330479434402e-01   │
│  goalie_saveSavesAgainst_away          │  5.923671437683795e-01   │
└────────────────────────────────────────┴──────────────────────────┘

```

Note, that these stats are printed out as part of the work done in TrainLinearRegression (see implementation details below for more information). If you add your own ML algorithms, any such information that you want provided will need to be implemented by you.

There is a predict option for the predict command that will conveniently list games based on the provided date filter.

![List games by date](https://raw.githubusercontent.com/MattRWallace/NHLPredictor/refs/heads/screenshots/screenshots/nhlpredictor_list.png)

When requesting a prediction, you can specify a specific game by the game ID which is in the listing.  You can also filter by date and get a determination for every game on that date.

![Predict a single game](https://raw.githubusercontent.com/MattRWallace/NHLPredictor/refs/heads/screenshots/screenshots/nhlpredictor_predict.png)

NOTE: Roster information is not added to the game object until the game actually starts which means that prior to that point, there is no data to make a prediction on. 

### Logs
Logging is provided by the logging package.  See src/nhl_predictor/shared/logging_config.py for the shared logging configuration. I use the [jog](https://github.com/qiangyt/jog) log viewer and have included, in source control, the configuration file I use for formatting those logs. To use, try `jog -f -c src/nhl_predictor/shared/config.jog.yaml buildData.log` from the repo root.

If you installed using pip instead of pulling the github repo yourself, you can download the config file directly from github or you can search in the site-packages folder where NHL-predictor was installed and locate it there; if you're unclear what that is, run `pip show NHL-predictor` and look at the Location property.

## Design

**Tech used**: Python, SQLite, SqliteDict, Pandas, SKLearn, Typer
The app is CLI only and there are 3 main commands that structure the behavior of the app: Build, Train and Predict. While there is more detailed documentation later in this document, I will briefly summarize them here.

### Components

#### Build
This fetches all the raw data from the NHL API and stores it locally in an SQLite database using the SqliteDict package for interfacing with the database itself. The only thing this command does is downloading and updating the data in the database.

#### Train
This is the step that actually builds a machine learning model.  There's two major components to be aware of: The ML algorithm implementation and what I'm calling the summarizer. Both of these components are consumed via dependency injection making the app adaptable. The summarizer is the product of a need to flatten all the player statistics into a smaller set of stats that pertain to a given game; it summarizes the individual stats for each player in a game into an overall roster score for that team in that game.  Similarly, when later trying to predict a future game outcome, we will want to summarize the past performance of each player listed on the game roster and use that when making our predictions. The summarizer is fully responsible for taking data persisted in the database and manipulating it into a data set appropriate for a ML algorithm to use.

#### Predict
This is the last step and hopefully the one you will be using the most.  The data has been downloaded and stored in a local database.  You have run the Train step and you now have a persisted file with your trained model saved on your disk.  You're now ready to see what predictions your model can produce. This command also lets you query and list games that are on the schedule for today which makes it a little bit easier to specify which games you want predicted.

#### Database design

## Implementation

### Build
Originally, I was fetching stats from the API and preprocessing the data during this step before storing all that data into CSV files.  This was a decent initial approach, but had a few limitations.

1. Data is processed before being stored. Once I was determined to decouple the algorithm and summarizer implementations from the base app, this preprocessing became a limitation for other summarizers or ML algorithms that want the raw data processed in a different way.
2. When I got to the implementation of the prediction logic, I discovered that the summary of stats that the NHL API provide at the end of each game and the set of stats it provides as a player's hisotrical record are different. The more granular game stats includes some influential stats (like number of hits) that are missing from the summary. I determined that I wanted to summarize a player's historical stats myself so that I could take advantage of the more granular stats which is when I first considered storing them in a local database.

### Train
TODO

### Predict
TODO

### Adding support for other machine learning algorithms
The application is designed so that additional ML algorithms can be added without too much effort.

The following steps are required to add a new algorithm:
1. Add the new algorithm to src/model/algorithms.py
2. Add a new file in each of src/trainer and src/predictor for your implementations (e.g. see src/trainer/linear_regression.py).
3. Add a case to the train method in src/trainer/trainer.py to invoke the training of your model.
4. Add a case to the _predict method in src/predictor/predictor.py to invoke the prediction with your model.
5. Implement your training and prediction logic.
**TODO** I need to add an abstract class to more clearly document how these files need to be designed.

### Adding new summarizers
As mentioned earlier, summarizers provide the logic to clean up and prepare the data for consumption by an ML algorithm.  For now there is only one summarizer implemented which performs a naive summation of most of the statistics for a particular game to get the overall roster strength. Depending on the need, a summarizer might be tied to a specific ML algorithm (e.g. if the algorithm has unique data needs, a custom summarizer is the place to do that). 

The following steps are required to add a new summarizer.
1. Create the new summarizer file in src/model/summarizers. Inherit from the Summarizer abstract class.
2. Add an entry to the SummarizerTypes enum in src/model/summarizer_manager.py and add a case to get_summarizer to create an instance of the new summarizer.  The string specified in the enum will be the name to use for the summarizer at the command line.
3. Implement the required methods from the Summarizer abstract class.