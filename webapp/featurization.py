

def addMatch(team, m, aggregates):    
    # initialize an empty record for the team if one doesn't already exist.        
    if team not in aggregates:       
        aggregates[team]= {
            'totalMatches':0, 
            'winCount': 0
        }
        for k in m.score_breakdown['blue'].keys():
            val = m.score_breakdown['blue'][k]
            if isinstance(val, int) or isinstance(val, bool):
                aggregates[team][f'{k}Total'] = 0
            elif isinstance(val, dict):
                pass
            elif isinstance(val, list):                
                pass

        for r in [1,2,3]:
            for v in ['Yes', 'No']:
                aggregates[team][f'autoLineRobot{r}{v}Total'] = 0
            for e in ['None', 'Parked', 'CenterStage', 'StageLeft', 'StageRight']:
                aggregates[team][f'endGameRobot{r}{e}Total'] = 0

    # update the stats for this team
    alliance = 'blue' if team in m.alliances.blue.team_keys else 'red'
    points = m.score_breakdown[alliance]
    #print(points)
    summary = aggregates[team]
    # update all of the fields.
    summary['totalMatches']+=1

    # TODO: figure out if we are robot 1, 2, or 3.
    for r in [1, 2, 3]:
        summary[f'autoLineRobot{r}{points[f"autoLineRobot{r}"]}Total'] += 1
        summary[f'endGameRobot{r}{points[f"endGameRobot{r}"]}Total'] += 1

    for k in points.keys():
        if isinstance(points[k], int):
            summary[f'{k}Total'] += points[k]
        elif isinstance(points[k], bool):
            summary[f'{k}Total'] += int(points[k])

    summary['winCount'] += int(m.winning_alliance==alliance)


# featurizeAlliances builds a feature vector for each alliance, by summing over the stats for each robot in the alliance.

def featurizeAlliances(teamAggregates, red, blue, label=0, comp_level='qm', event='none'):
    match_features = { 'red_missingCount':0, 'blue_missingCount': 0 }
    count=0    
    allKeys = set()
    for t in red:
        if t not in teamAggregates:
            match_features['red_missingCount']+=1
            continue
        for k in teamAggregates[t]:
            key = 'red_'+k
            if key not in match_features:
                match_features[key]=0
            match_features[key]+=teamAggregates[t][k]
            allKeys.add(key)
        count+=1
    # compute the average
    for k in allKeys:
        match_features[k]/=count
    count=0
    allKeys=set()
    for t in blue:
        if t not in teamAggregates:
            match_features['blue_missingCount']+=1
            continue
        for k in teamAggregates[t]:
            key = 'blue_'+k
            if key not in match_features:
                match_features[key]=0
            match_features[key]+=teamAggregates[t][k]
            allKeys.add(key)
        count+=1
    # compute the average
    for k in allKeys:
        match_features[k]/=count
    match_features['event']= event
    match_features['comp_level']= comp_level
    match_features['label']= label #int(m.winning_alliance=='red')    
    return match_features

def featurizeMatch(m, teamAggregates):
    return featurizeAlliances(teamAggregates,
        m.alliances.red.team_keys, 
        m.alliances.blue.team_keys, 
        label=int(m.winning_alliance=='red'),
        event = m.event_key, comp_level=m.comp_level)

def invertMatch(f):
    f2={}
    for k in f:
        k2 = k.replace('red_','temp_').replace('blue_','red_').replace('temp_','blue_')
        f2[k2]=f[k]
    f2['label']=1-f['label']
    return f2
