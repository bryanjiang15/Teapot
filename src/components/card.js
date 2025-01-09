import React from 'react'
import './card.css';
import { useDrag } from 'react-dnd'


const Card = ({card}) => {
  const [{isDragging}, dragRef] = useDrag({
    type: 'CARD',
    item: {card: card},
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  return (
    <div 
      ref={dragRef}
      style={{
        opacity: isDragging ? 0.5 : 1,
        cursor: 'move',
      }}
      className='char-card'
    >
        <div className='health-power'>
          <p className='health'>{card.health}</p>
          <p className='power'>{card.power}</p>
        </div>
        <div className='picture'>
            <h1 className='emoji'>{card.emoticon}</h1>
        </div>
        <div className='name'>
          <p>{card.name}</p>
        </div>
    </div>
  )
}

export default Card