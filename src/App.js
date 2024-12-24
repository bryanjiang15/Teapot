// import logo from './logo.svg';
import './App.css';
import { get_combined_word } from './llama.js';
import { useState } from 'react';

import Drag from './components/Drag.js';
import DropArea from './components/Drop.js';

import { DndProvider } from 'react-dnd'
import { HTML5Backend } from 'react-dnd-html5-backend'
import axios from 'axios';


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
    "name" : "japan",
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
  },
  {
    "id" : 7,
    "health": 777,
    "power": 8,
    "name" : "spongebob",
    "emoticon" : "🧽"
  },]);

  const [id, setId] = useState(7);

  const handleDrop = async (item) => {



    let temp = cards.slice();
    // temp.forEach(card => {
    //   if(card==item.card){
    //     const index = temp.indexOf(card);
    //     temp.splice(index, 1);
    //   }
    // });

    setCards(temp);
    setDropped([...droppedItem, item]);
    
    if(droppedItem.length==1){
      const cleared = [];
      setDropped(cleared);

      //let card = await get_combined_word(item.card.name, droppedItem[0].card.name, id, setId, setCards, temp);
      const response = await axios.post('http://localhost:3001/', {
        first: item.card.name,
        second: droppedItem[0].card.name
      })
      let word = response.data;
      console.log(word);

      const card_response = await axios.post('http://localhost:3001/new-card', {
        word: word.result
      })
      let card = card_response.data;
      console.log(card);
      // console.log(card);
      // temp.push(card);
      // console.log(temp);
    }

    //setCards(temp);
    
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

