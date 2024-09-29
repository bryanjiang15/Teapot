import React from 'react'
import './Card.css';

const Card = ({card}) => {
  return (
    <div className='char-card'>
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