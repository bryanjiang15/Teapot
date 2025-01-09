import { useDrop } from 'react-dnd';
import Card from './Card.js';
import { useState } from 'react';

export default function DropArea({ onCombineCards }) {
  const [droppedCards, setDroppedCards] = useState([]);

  const [{ isOver }, drop] = useDrop({
    accept: 'CARD',
    drop: (item) => {
      setDroppedCards((prev) => {
        const newCards = [...prev, item];
        if(newCards.length === 2) {
          onCombineCards(newCards);
          return [];
        }else{
          return newCards;
        }
      });
    },
    collect: (monitor) => ({
      isOver: monitor.isOver(),
    }),
  });

  return (
    <div
      ref={drop}
      style={{
        height: '',
        width: '100%',
        backgroundColor: isOver ? 'lightgreen' : 'lightblue',
        padding: '16px',
      }}
    >
      <h1>Drop here</h1>
      <div>
        {
            droppedCards.map((item, index) => (
                <Card key = {item.card.id} card = {item.card}></Card>
            ))
        }
      </div>
    </div>
  );
}