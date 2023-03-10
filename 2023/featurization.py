

def addMatch(team, m, aggregates):    
    # initialize an empty record for the team if one doesn't already exist.        
    if team not in aggregates:       
        aggregates[team]= {
            'totalMatches':0, 
            'winCount': 0
        }
        for k in m.score_breakdown['blue'].keys():
            val = m.score_breakdown['blue'][k]
            if type(val) is int or type(val) is bool:
                aggregates[team][f'{k}Total'] = 0
            elif type(val) is dict:
                for f in ['B','M','T']:
                    for e in ['Cone','Cube']:
                        for i in range(9):
                            aggregates[team][f'{k}.{f}.{e}.{i}.Total'] = 0
            elif type(val) is list:
                # TODO: links
                pass
            
        for r in [1,2,3]:
            for v in ['Yes', 'No']:
                aggregates[team][f'mobilityRobot{r}{v}Total'] = 0
            for e in ['None', 'Docked', 'Park']:
                aggregates[team][f'endGameChargeStationRobot{r}{e}Total'] = 0 
                if e=='Park':
                    continue # parked doesn't apply to autonomous
                aggregates[team][f'autoChargeStationRobot{r}{e}Total'] = 0 
        for e in ['Level', 'NotLevel']:
            aggregates[team][f'endGameBridgeState{e}Total'] = 0
            aggregates[team][f'autoBridgeState{e}Total'] = 0
            
                
        
    # update the stats for this team
    alliance = 'blue' if team in m.alliances.blue.team_keys else 'red'
    points = m.score_breakdown[alliance]
    #print(points)
    summary = aggregates[team]
    # update all of the fields.
    summary['totalMatches']+=1    
    
    # TODO: figure out if we are robot 1, 2, or 3.
    for r in [1, 2, 3]:        
        summary[f'mobilityRobot{r}{points[f"mobilityRobot{r}"]}Total'] += 1
        summary[f'endGameChargeStationRobot{r}{points[f"endGameChargeStationRobot{r}"]}Total'] += 1
        summary[f'autoChargeStationRobot{r}{points[f"autoChargeStationRobot{r}"]}Total'] += 1
    summary[f'endGameBridgeState{points["endGameBridgeState"]}Total'] += 1
    summary[f'autoBridgeState{points["autoBridgeState"]}Total'] += 1
    
    for k in ['B','M','T']:
        for i in range(9):
            for f in ['teleop','auto']:
                v = points[f'{f}Community'][k][i]
                if v == 'None':
                    continue
                aggregates[team][f'{f}Community.{k}.{v}.{i}.Total'] += 1
    
    for k in points.keys():
        if type(points[k]) is int:
            summary[f'{k}Total'] += points[k]
        elif type(points[k]) is bool:
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
