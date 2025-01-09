import React from 'react';
import Card from './Card.js';

const CardList = ({cards}) => {
    return (
        <div className='card-container column-div width-right'>
            {cards.map((item, index) => (
            <Card key={item.id} card = {item}></Card>
            ))}
        </div>
    )
}

export default CardList;