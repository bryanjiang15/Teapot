// import logo from './logo.svg';
import './App.css';
// import { get_combined_word } from './llama.js';
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
    ["fire", 1],
    ["water", 2],
    ["earth", 3]
  ]));

  const [cards, setCards] = useState([{
    "health": 2,
    "power": 1,
    "name" : "rat",
    "emoticon" : "🐀"
  },
  {
    "health": 1,
    "power": 6,
    "name" : "big mountain",
    "emoticon" : "🗻"
  },
  {
    "health": 3,
    "power": 3,
    "name" : "moyai",
    "emoticon" : "🗿"
  },
  {
    "health": 10000,
    "power": 50000,
    "name" : "fucking japan",
    "emoticon" : "🗾"
  },
  {
    "health": 5,
    "power": 1,
    "name" : "a bus stop",
    "emoticon" : "🚏"
  },
  {
    "health": 7,
    "power": 7,
    "name" : "skibidi",
    "emoticon" : "🚽"
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

    const temp = cards.slice();
    temp.forEach(card => {
      if(card==item.card){
        console.log(card.name+" "+item.card.name);
        const index = temp.indexOf(card);
        temp.splice(index, 1);
      }
    });
    console.log("did not find "+item.card.name);

    setCards(temp);
    setDropped([...droppedItem, item.text]);

    console.log(temp);
  }


  return (
    <div className="App">
      <div className='row-div'>
          <DndProvider backend={HTML5Backend}>
            {/* <div className='width-max'>
              {
                Array.from(cardsOwned.entries()).map((item, index) => (
                  <Drag isDragging={true} key={index} card={{
                    "health": 1,
                    "power": 6,
                    "name" : "big mountain",
                    "emoticon" : "🗻"
                  }}></Drag> 
                ))
              }
            </div> */}

            <DropArea onDrop={handleDrop} droppedArr={droppedItem}>
            </DropArea>

            <div className='card-container column-div width-right'>
              {cards.map((item, index) => (
                <Drag isDragging={true} key={index} card = {item}></Drag>
              ))}
            </div>
          </DndProvider>
      </div>
    </div>
  );
}

export default App;
