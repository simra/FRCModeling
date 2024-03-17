import React, { useEffect, useState } from 'react';
import { Team, TeamStats } from '../types/TeamTypes'; 
import { validateLocaleAndSetLanguage } from 'typescript';

function EventForm({ onTeamsUpdate }: { onTeamsUpdate: (district: string, model_event: string, matchType: string, teams: Team[]) => void }) {
  const [district, setDistrict] = useState(localStorage.getItem('district') || '');
  const [modelEvent, setModelEvent] = useState(localStorage.getItem('modelEvent') || '');
  const [matchType, setMatchType] = useState(localStorage.getItem('matchType') || '');
  const [predictionEvent, setPredictionEvent] = useState(localStorage.getItem('predictionEvent') || '');
  //const [teams, setTeams] = useState<Team[]>([]);

    useEffect(() => {
        localStorage.setItem('district', district);
        localStorage.setItem('modelEvent', modelEvent);
        localStorage.setItem('matchType', matchType);
        localStorage.setItem('predictionEvent', predictionEvent);
    }, [district, modelEvent, matchType, predictionEvent]);

  const handleSubmit = (event: React.FormEvent): void => {
    event.preventDefault();
    // Set the model key and fetch the team names for the prediction event
    let baseUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';
    let url = `${baseUrl}/model/${district}_${modelEvent}_${matchType}/event/${predictionEvent}/teams`;
    console.log(url);
    fetch(url)
      .then(response => response.json())
      .then(data => {
        onTeamsUpdate(district, modelEvent, matchType, data);
      });
  };

  return (
    <form onSubmit={handleSubmit} className="event-form">
        <div className="form-group">
      <label>
        District: </label>
        <input type="text" value={district} onChange={e => setDistrict(e.target.value) } className="input-field" /><br></br>
     
      </div>
      <div className="form-group">
      <label>
        Model Event: </label>
        <input type="text" value={modelEvent} onChange={e => setModelEvent(e.target.value) } className="input-field" /><br></br>
     
      </div>
      <div className="form-group">
      <label>
        Match Type:</label>
        <input type="text" value={matchType} onChange={e => setMatchType(e.target.value)} className="input-field" /><br></br>
      
      </div>
      <div className="form-group">
      <label>
        Prediction Event: </label>
        <input type="text" value={predictionEvent} onChange={e => setPredictionEvent(e.target.value)} className="input-field" /><br></br>
     
      </div>
      <button type="submit">Submit</button>
    </form>
  );
}

export default EventForm;