import logo from './logo.svg';
import './App.css';
import Card from './components/Card' 
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
          <Drag isDragging={true} text={'hello1'}></Drag>
          <Drag isDragging={true} text={'hello2'}></Drag>
          <Drag isDragging={true} text={'hello3'}></Drag>
        </div>

        <DropArea onDrop={handleDrop}></DropArea>
      </DndProvider>

    </div>
  );
}

export default App;
