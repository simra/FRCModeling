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

## Match Data Caching

The backend uses an **incremental, file-based cache** (`matches_<district>_<year>.pkl`) to avoid
redundant round-trips to The Blue Alliance (TBA).

### How it works

1. On the first run the full events list and all per-event matches/teams are fetched from TBA and
   written to disk.
2. On subsequent runs the existing pickle file is loaded and the HTTP `If-Modified-Since` header
   is used for every request:
   - The events-list endpoint gets the *global* `Last-Modified` value saved with the cache.
   - Each event's matches/teams endpoint gets a **per-event** `Last-Modified` value stored in
     `result['event_last_modified']`.  Events that TBA has not updated since the last fetch
     return HTTP 304 Not Modified and keep their cached data untouched.
3. A backup of the previous pickle is kept at `<file>.bak` before each write.
4. The `/model/<key>/refresh` API endpoint triggers a full incremental re-fetch and rebuilds
   the in-memory model.

Pass `--reset` (CLI) or call `fetch_all_matches(reset=True)` to force a complete re-fetch,
ignoring all cached timestamps.

### Persisting the cache across deployments

The pickle cache is a local file, which is **ephemeral on most PaaS platforms** (e.g., Azure App
Service restarts wipe the local filesystem).  To retain the cache between deployments, choose
one of the following strategies:

| Option | Effort | Notes |
|---|---|---|
| **Persistent volume / Azure Files mount** | Low | Set the `DATA_FOLDER` env-var to the mount path. No code changes required. Recommended for Azure App Service. |
| **Azure Blob Storage** | Medium | Add `azure-storage-blob`; download the pkl on startup and upload after each fetch. Survives deployments and scales to multiple instances. |
| **Object storage (AWS S3 / GCS)** | Medium | Same pattern as Azure Blob using `boto3` / `google-cloud-storage`. |
| **SQLite / relational DB** | High | Replace pickle with structured storage; enables partial row-level updates but requires a schema migration. |

The simplest production path is to **mount an Azure Files share** and set
`DATA_FOLDER=/mnt/data` so the existing pickle-based logic works without any code change.

