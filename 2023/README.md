# Rapid React Modeling

## Steps:
1. `python fetchMatches.py --year 2023 --reset`

    This will pull all the data for 2023.

    You can optionally pass --reset to re-pull all the data, and --year YEAR to pull data for a year other than 2023.  

2. This has not been updated for 2023: 

    `python fetchEventStatuses.py --events [event names comma-separated]`
    
    Fetches event rankings to include in stats_2023.tsv


2. MoreFeatures.ipynb has been updated for 2022:

    `jupyter notebook`
    
    This will launch the notebook browser. Open MoreFeatures.ipynb and run the notebook to rebuild the model.

    TODO: update the notebook to produce some ratings per-team, and predict strong alliances.

## Server: 
Not yet updated:
1. cd 2020
2. python server.py