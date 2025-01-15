import React from 'react';
import logo from './logo.svg';
import './App.css';
import EventForm from './components/EventForm'; // Import the EventForm component
import AllianceComponent from './components/AllianceComponent';


function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1> Playoff Bracket Simulator </h1>
      </header>
      <main>
      <AllianceComponent />
      </main>      
    </div>
  );
}

export default App;
