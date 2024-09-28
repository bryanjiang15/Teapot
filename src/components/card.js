import React from 'react'
import './Card.css';

const Card = ({health, power, name}) => {
  return (
    <div className='char-card'>
        <div className='health-power'>
          <p className='health'>{health}</p>
          <p className='power'>{power}</p>
        </div>
        <div className='picture'>
            <h1 className='emoji'>&#128000;</h1>
        </div>
        <div className='name'>
          <p>{name}</p>
        </div>
    </div>
  )
}

export default Card