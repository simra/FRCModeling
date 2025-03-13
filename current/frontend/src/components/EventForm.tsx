import React, { useEffect, useState } from 'react';
import { Team } from '../types/TeamTypes'; 
import moment from 'moment-timezone';

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

  useEffect(() => {        
    localStorage.setItem('predictionEvent', predictionEvent);
  }, [district, modelEvent, matchType, predictionEvent]);

  const handleSubmit = (event: React.FormEvent): void => {
    event.preventDefault();
    let baseUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';
    let url = `${baseUrl}/model/${district}_${modelEvent}_${matchType}/event/${predictionEvent}/teams`;
    console.log(url);
    fetch(url)
      .then(response => response.json())
      .then(data => {
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

  const formatTimestamp = (timestamp: string) => {
    return moment.tz(timestamp, 'UTC').tz('America/Los_Angeles').format('YYYY-MM-DD HH:mm:ss z');
  };

  return (
    <form onSubmit={handleSubmit} className="event-form">
      <div className="form-group">
        <label>District:</label>
        <input type="text" value={district} onChange={e => onPropUpdate(e.target.value, modelEvent, matchType)} className="input-field" /><br />
      </div>
      <div className="form-group">
        <label>Model Event:</label>
        <input type="text" value={modelEvent} onChange={e => onPropUpdate(district, e.target.value, matchType)} className="input-field" /><br />
      </div>
      <div className="form-group">
        <label>Match Type:</label>
        <input type="text" value={matchType} onChange={e => onPropUpdate(district, modelEvent, e.target.value)} className="input-field" /><br />
      </div>
      <div className="form-group">
        <label>Prediction Event:</label>
        <input type="text" value={predictionEvent} onChange={e => setPredictionEvent(e.target.value)} className="input-field" /><br />
      </div>
      <button type="submit">Submit</button>
      <div><i>Last model update: {modelTimestamp ? formatTimestamp(modelTimestamp) : ""}</i></div>
    </form>
  );
}

export default EventForm;