import logo from './logo.svg';
import './App.css';
import { get_combined_word } from './llama.js';
import Card from './components/card' 
import { useState } from 'react';

import Drag from './components/Drag';
import DropArea from './components/Drop';

import { DndProvider } from 'react-dnd'
import { HTML5Backend } from 'react-dnd-html5-backend'


// import Drag from './components/Drag'

function App() {

  const [droppedItem, setDropped] = useState([]);

  const [cards, setCards] = useState([{
    "health": 1,
    "power": 1,
    "name" : "rat"
  }]);

  const handleDrop = (item) => {
    const droppedArr = [...droppedItem, item];

    setDropped(droppedArr);
    console.log("Dropped item", item);
    return get_combined_word("Fire", "Rain");
  }


  return (
    <div className="App">
      <DndProvider backend={HTML5Backend}>
        <div className='card-container'>
          {cards.map((item, index) => (
            <Card key={index} health = {item.health} power = {item.power} name = {item.name}></Card>
          ))}
        </div>

        <div>
          <Drag isDragging={true} text={'water'}></Drag>
          <Drag isDragging={true} text={'fire'}></Drag>
          <Drag isDragging={true} text={'earth'}></Drag>
          <Drag isDragging={true} text={'air'}></Drag>
        </div>

        <DropArea onDrop={handleDrop}></DropArea>
      </DndProvider>

    </div>
  );
}

export default App;
