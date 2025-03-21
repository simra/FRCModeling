import React, { useEffect, useState } from 'react';
import { Team, TeamStats } from '../types/TeamTypes'; 
import { validateLocaleAndSetLanguage } from 'typescript';

class EventFormProps {
  onTeamsUpdate: (district: string, model_event: string, matchType: string, teams: Team[]) => void;
  onPropUpdate: (district: string, model_event: string, matchType: string) => void;
  district: string;
  modelEvent: string;
  matchType: string;

  constructor(onTeamsUpdate: (district: string, model_event: string, matchType: string, teams: Team[]) => void, onPropUpdate: (district: string, model_event: string, matchType: string) => void, district: string, modelEvent: string, matchType: string) {
    this.onTeamsUpdate = onTeamsUpdate;
    this.onPropUpdate = onPropUpdate;
    this.district = district;
    this.modelEvent = modelEvent;
    this.matchType = matchType;
  }
}

function EventForm({ onTeamsUpdate, onPropUpdate, district, modelEvent, matchType }: EventFormProps) {
  const [predictionEvent, setPredictionEvent] = useState(localStorage.getItem('predictionEvent') || '');
  const [modelTimestamp, setModelTimestamp] = useState(localStorage.getItem('modelTimestamp') || '');
  //const [teams, setTeams] = useState<Team[]>([]);

    useEffect(() => {        
        localStorage.setItem('predictionEvent', predictionEvent);
    }, [district, modelEvent, matchType, predictionEvent]);

  const handleSubmit = (event: React.FormEvent): void => {
    event.preventDefault();
    // Set the model key and fetch the team names for the prediction event
    let baseUrl = (process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000').replace(/\/+$/, '');
    let url = `${baseUrl}/model/${district}_${modelEvent}_${matchType}/event/${predictionEvent}/teams`;
    console.log(url);
    fetch(url)
      .then(response => response.json())
      .then(data => {
        // deduplicate data based on team number
        let teams: Team[] = [];
        let teamKeys: string[] = [];
        data.forEach((team: Team) => {
          if (!teamKeys.includes(team.team)) {
            teams.push(team);
            teamKeys.push(team.team);
          }
        });
        onTeamsUpdate(district, modelEvent, matchType, teams);
      });
    let ts_url = `${baseUrl}/model/${district}_${modelEvent}_${matchType}`;
    fetch(ts_url)
      .then(response => response.json())
      .then(data => {
        setModelTimestamp(data['last_modified']);
      });
  };

  return (
    <form onSubmit={handleSubmit} className="event-form">
        <div className="form-group">
      <label>
        District: </label>        
        <input type="text" value={district} onChange={e => onPropUpdate(e.target.value, modelEvent, matchType) } className="input-field" /><br></br>
     
      </div>
      <div className="form-group">
      <label>
        Model Event: </label>
        <input type="text" value={modelEvent} onChange={e => onPropUpdate(district, e.target.value, matchType) } className="input-field" /><br></br>
     
      </div>
      <div className="form-group">
      <label>
        Match Type:</label>
        <input type="text" value={matchType} onChange={e => onPropUpdate(district, modelEvent, e.target.value)} className="input-field" /><br></br>
      
      </div>
      <div className="form-group">
      <label>
        Prediction Event: </label>
        <input type="text" value={predictionEvent} onChange={e => setPredictionEvent(e.target.value)} className="input-field" /><br></br>
     
      </div>
      <button type="submit">Submit</button>
      <div><i>Last model update: {modelTimestamp ? modelTimestamp : ""}</i></div>
    </form>
  );
}

export default EventForm;