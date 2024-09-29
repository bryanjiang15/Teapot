// import logo from './logo.svg';
import './App.css';
// import { get_combined_word } from './llama.js';
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
    "id" : 1,
    "health": 2,
    "power": 1,
    "name" : "rat",
    "emoticon" : "🐀"
  },
  {
    "id" : 2,
    "health": 1,
    "power": 6,
    "name" : "big mountain",
    "emoticon" : "🗻"
  },
  {
    "id" : 3,
    "health": 3,
    "power": 3,
    "name" : "moyai",
    "emoticon" : "🗿"
  },
  {
    "id" : 4,
    "health": 10000,
    "power": 50000,
    "name" : "fucking japan",
    "emoticon" : "🗾"
  },
  {
    "id" : 5,
    "health": 5,
    "power": 1,
    "name" : "a bus stop",
    "emoticon" : "🚏"
  },
  {
    "id" : 6,
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
        const index = temp.indexOf(card);
        temp.splice(index, 1);
      }
    });

    setCards(temp);
    setDropped([...droppedItem, item]);
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
                <Drag isDragging={true} key={item.id} card = {item}></Drag>
              ))}
            </div>
          </DndProvider>
      </div>
    </div>
  );
}

export default App;
