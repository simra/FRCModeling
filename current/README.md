# FRC Modeling

## Setup

1. `git clone https://github.com/simra/FRCModeling`
2. `cd FRCModeling`
3. `git checkout simra/2025`
4. Install Anaconda Python from here: https://www.anaconda.com/download
5. In the VS Code terminal, `conda create --name frcmodeling python=3.10`
6. `conda activate frcmodeling`
7. `pip install -r requirements.txt`
8. `cd current`

## Steps to pull/update data and model:
1. `python fetchMatches.py --year 2024 --reset`

    This will pull all the data for 2024.

    You can optionally pass --reset to re-pull all the data, and --year YEAR to pull data for a year other than 2024.  

2. `runScoutingReport.py`

## Web page: 
    - backend\  - python flask app - see deploy.sh for build/deploy steps
    - frontend\ - react front-end

## Installation
1. Install node.js on your machine from https://nodejs.org/en/download/
2. Open a command prompt `cd current\frontend` 
3. run `npm install` and then `npm run build`
4. Delete `backend\static\build` if it exists
5. Copy the contents of `build` to `backend\static\build`
6. `cd ..\backend`
7. `pip install -r requirements.txt`
8. `python -m flask run`




## Model Code

Model generation is in OPR.py.  See runScoutingReport for an example of how it's used.

