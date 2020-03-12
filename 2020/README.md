# Infinite Recharge Modeling

## Steps:
1. python fetchMatches.py

    You can optionally pass --reset to re-pull all the data, and --year YEAR to pull data for a year other than 2020.  

2. python fetchEventStatuses.py --events [event names comma-separated]
    
    Fetches event rankings to include in stats_2020.tsv


2. jupyter notebook
    
    This will launch the notebook browser. Open MoreFeatures.ipynb and run the notebook to rebuild the model.


## Server: 
1. cd 2020
2. python server.py