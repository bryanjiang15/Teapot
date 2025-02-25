import React from 'react'
import './card.css';
import { useDrag } from 'react-dnd'


const Card = ({card}) => {
  const [{isDragging}, drag] = useDrag({
    type: 'CARD',
    item: {card: card},
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  return (
    <div 
      ref={drag}
      className={`card ${isDragging ? 'dragging' : ''}`}
    >
      <div className="card-emoticon">{card.emoticon}</div>
      <div className="card-name">{card.name}</div>
      <div className="card-stats">
        <span className="power">{card.power}</span>
        <span className="health">{card.health}</span>
      </div>
    </div>
  )
}

export default Card