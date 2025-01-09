// import logo from './logo.svg';
import './App.css';
import { useCallback, useState } from 'react';

import DropArea from './components/Drop.js';

import { DndProvider } from 'react-dnd'
import { HTML5Backend } from 'react-dnd-html5-backend'
import axios from 'axios';
import Card from './components/Card.js';
import CardList from './components/CardList.js';
import { debounce } from 'lodash';


// import Drag from './components/Drag'

function App() {

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
    "name" : "mountain",
    "emoticon" : "🗻"
  },
  {
    "id" : 3,
    "health": 3,
    "power": 3,
    "name" : "google",
    "emoticon" : "🔍"
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
    "name" : "bus stop",
    "emoticon" : "🚏"
  },
  {
    "id" : 6,
    "health": 7,
    "power": 7,
    "name" : "water",
    "emoticon" : "🌊"
  },
  {
    "id" : 7,
    "health": 777,
    "power": 8,
    "name" : "fire",
    "emoticon" : "🔥"
  },]);

  const [id, setId] = useState(7);

  const combineCards = debounce(async (dropped) => {
    //let card = await get_combined_word(item.card.name, droppedItem[0].card.name, id, setId, setCards, temp);
    const response = await axios.post('http://localhost:3001/', {
      first: dropped[0].card.name,
      second: dropped[1].card.name
    })
    let word = response.data;
    console.log(word);

    const card_response = await axios.post('http://localhost:3001/new-card', {
      word: word.result
    })
    let card = card_response.data;
    console.log(card);

    setId(id + 1);

    card = {
      "id" : id+1,
      "health": card.health,
      "power": Math.floor(Math.random() * (100 - 10 + 1)) + 10,
      "name" : card.name,
      "emoticon" : word.emoji
    }

    cards.unshift(card);
    setCards([...cards]);
    console.log(cards);
    

    //setCards(temp);
    
  }, 100, { leading: true, trailing: false });


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

            <DropArea onCombineCards={combineCards}>
            </DropArea>
            <CardList cards={cards}></CardList>
          </DndProvider>
      </div>
    </div>
  );
}

export default App;

