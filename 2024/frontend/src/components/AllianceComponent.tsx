import React, { useState, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable, DroppableProvided, DraggableProvided, DroppableProps, DropResult, DroppableStateSnapshot } from 'react-beautiful-dnd';
import { scaleLinear } from 'd3-scale';
import EventForm from './EventForm';
import { Team } from '../types/TeamTypes';
import { Alliance } from '../types/Alliance';
import AllianceRender from './AllianceRender';
import StrictModeDroppable from './StrictModeDroppable';

function AllianceComponent() {
  const [district, setDistrict] = useState('');
  const [model_event, setModelEvent] = useState('');
  const [match_type, setMatchType] = useState('');
  const [density, setDensity] = useState<{[key: number]: {[key: string]: number} }>({});
  const [overall, setOverall] = useState<{[key: string]: number}>({});

  const [leftTeams, setLeftTeams] = useState<Team[]>(
    () => {const savedTeams = localStorage.getItem('teams');
    return savedTeams ? JSON.parse(savedTeams) : [];}
  );
  
  // we will move these to a separate component
  const [slots, setSlots] = useState<Array<Array<{ team: Team | null }>>>( () => {
    const savedSlots = localStorage.getItem('slots');
    return savedSlots ? JSON.parse(savedSlots) : Array.from({ length: 8 }, () => [{ team: null }, { team: null }, { team: null }]);
  });

  useEffect(() => {
    localStorage.setItem('teams', JSON.stringify(leftTeams));
  }, [leftTeams]);
  
  useEffect(() => {
    localStorage.setItem('slots', JSON.stringify(slots));
  }, [slots]);

  const handleTeamsUpdate = (district: string, model_event: string, match_type: string, teams: Team[]) => {
    setLeftTeams(teams);
    setDistrict(district);
    setModelEvent(model_event);
    setMatchType(match_type);
  };

  const updateBrackets = () => {
    // map slots to a json payload formatted {A1: [team1, team2, team3], A2: [team4, team5, team6], ...}
    var payload = slots.reduce<{[key: string]: string[]}>((acc, alliance, index) => {
      acc['A' + (index + 1)] = alliance.map(slot => slot.team ? slot.team.team : '');
      return acc;
    }, {});
    console.log(payload);
    // POST alliances to /model/district_model_event_match_type/bracket
    let baseUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';
    let url = `${baseUrl}/model/${district}_${model_event}_${match_type}/bracket`;
    // POST the alliances to the url using fetch:
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    }).then(response => response.json())
    .then(data => {
      console.log(data);
      setDensity(data['density']);
      setOverall(data['overall']);
    });

  }

  const handleDragEnd = (result: any) => {
    console.log('drag end', result.destination);
    const { source, destination } = result;
    if (!destination) {
      return;
    }

    if (source.droppableId === 'left' && destination.droppableId.startsWith('droppable-')) {
      const team = leftTeams[source.index];
      let newTeams = leftTeams.filter((_, index) => index !== source.index);
      let row = parseInt(destination.droppableId.split('-')[1])-1;
      let col = parseInt(destination.droppableId.split('-')[2]);
      const destinationSlot = slots[row][col];
      if (destinationSlot.team) {
        // If it does, remove that team from the slots and add it back to the leftTeams array
        newTeams = [...newTeams, destinationSlot.team as Team];
      }
      setLeftTeams(newTeams);
      setSlots(slots.map((alliance, index) => (index === row) ? 
        alliance.map((slot,index2) => index2 === col ? {team: team } : slot) : alliance));
    }
  };

  return (
    <DragDropContext onDragEnd={handleDragEnd}>
      <EventForm onTeamsUpdate={handleTeamsUpdate} />
      <div className='alliance-component'>
        <StrictModeDroppable droppableId="left">
          {(provided: DroppableProvided) => (
            <div ref={provided.innerRef} {...provided.droppableProps} className="team-list">
              {
                (leftTeams.length > 0) ? (
                  (() => {
                    let colorScale = scaleLinear<string>()
                      .domain([Math.min(...leftTeams.map(team => team.stats.opr)), Math.max(...leftTeams.map(team => team.stats.opr))])
                      .range(['lightgreen', 'red']);                   
                    return leftTeams.sort((a, b) => b.stats.opr - a.stats.opr).map((team, index) => { 
                      let calcBackgroundColor = colorScale(team.stats.opr)
                      
                      return (
                      <Draggable key={team.team} draggableId={team.team} index={index}>
                        {(provided: DraggableProvided) => { 
                          const style = {
                            backgroundColor: calcBackgroundColor,                      
                            ...provided.draggableProps.style,
                        } ;
                          return (<div ref={provided.innerRef} {...provided.draggableProps} {...provided.dragHandleProps} style={style} title={team.stats.opr.toString()} className="team-div" >                            
                            {team.team}
                          </div>)
                        }
                        }
                      </Draggable>
                    )})
                  })()) : <div>Click submit to load event teams</div>
              }
              {provided.placeholder}
            </div>
          )}
        </StrictModeDroppable>
        <div className='alliance-list'>
        {Array.from({ length: 8 }, (_, i) => i + 1).map(id => (
        <div key={id} className='alliance-slots'>
          <div style={{ marginRight: '10px' }}>A{id}</div>
          {slots[id-1].map((slot, index) => (
            <StrictModeDroppable key={index} droppableId={`droppable-${id}-${index}`}>
              {(provided : DroppableProvided, snapshot: DroppableStateSnapshot) => (
                <div
                  ref={provided.innerRef}
                  style={{ backgroundColor: snapshot.isDraggingOver ? 'lightblue' : 'lightgrey' }}
                  {...provided.droppableProps}
                  className = 'alliance-slot'
                >
                  {slot.team? slot.team.team : 'Drop team here'}
                  {provided.placeholder}
                </div>
              )}
            </StrictModeDroppable>
          ))}
          <div className='overall-value'>{overall && ('A'+id) in overall ? overall['A'+id]/10 : ''}</div>
          </div>))}
          <button onClick={updateBrackets}>Run Brackets</button>
        </div>
        <div className='bracket-list'>
                {density && Object.keys(density).map((match)=> {
                  let outcome = density[Number(match)];
                  return (
                    <div>M{match}: {Object.keys(outcome).map((key) => ` ${key}: ${outcome[key]/10}` )}
                  </div>)})}
        </div>
        </div>
    </DragDropContext>
  );
}

export default AllianceComponent;