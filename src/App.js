import logo from './logo.svg';
import './App.css';
import Card from './components/Card' 
import { useState } from 'react';

function App() {

  const [cards, setCards] = useState([{
    "health": 1,
    "power": 1,
    "name" : "rat"
  }]);


  return (
    <div className="App">
      {/* <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header> */}

      <div className='card-container'>
        {cards.map((item, index) => (
          <Card key={index} health = {item.health} power = {item.power} name = {item.name}></Card>
        ))}
      </div>

    </div>
  );
}

export default App;
