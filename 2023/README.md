# Rapid React Modeling

## Steps:
1. `python fetchMatches.py --year 2023 --reset`

    This will pull all the data for 2023.

    You can optionally pass --reset to re-pull all the data, and --year YEAR to pull data for a year other than 2023.  

2. MoreFeatures.ipynb is the main ML notebook, useful for exploring the data and training a machine learning model.  It is now updated for 2023.

    `jupyter notebook`

    This will launch the notebook browser. Open MoreFeatures.ipynb and run the notebook to rebuild the model.


3. Rankings.ipynb is a notebook for ranking alliance partners. This will be our main notebook once the ML model is ready. This isn't updated for 2023 yet.



4. This has not been updated for 2023: 

    `python fetchEventStatuses.py --events [event names comma-separated]`
    
    Fetches event rankings to include in stats_2023.tsv

## Server: 
Not yet updated:
1. cd 2023
2. python server.py