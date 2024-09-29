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

  const [cardsOwned, setOwned] = useState(new Map([
    ["hello1", 1],
    ["hello2", 1],
    ["hello3", 1]
  ]));

  const [cards, setCards] = useState([{
    "health": 1,
    "power": 1,
    "name" : "rat"
  }]);

  const handleDrop = (item) => {

    // const droppedMap = new Map(droppedItem);

    // if(droppedMap.has(item.text)){
    //   let temp = droppedMap.get(item.text) + 1;

    //   droppedMap.set(item.text, temp);
    // }

    // else{
    //   droppedMap.set(item.text, 1);
    // }

    // setDropped(droppedMap);

    const temp = new Map(cardsOwned);
    temp.delete(item.text);

    setOwned(temp);
    setDropped([...droppedItem, item.text]);

    console.log(temp);
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
          {
            Array.from(cardsOwned.entries()).map((item, index) => (
              <Drag isDragging={true} key={index} text={item[0]}></Drag> 
            ))
          }
        </div>

        <DropArea onDrop={handleDrop} droppedArr={droppedItem}>
        </DropArea>
      </DndProvider>

    </div>
  );
}

export default App;
