import React from 'react';
import { useDrop } from 'react-dnd';
import Card from './Card.js';
import './BoardSlot.css';

const BoardSlot = ({ card, slotIndex, onDrop }) => {
    const [{ isOver }, drop] = useDrop(() => ({
        accept: 'CARD',
        drop: (item) => onDrop(item.index, slotIndex),
        collect: (monitor) => ({
            isOver: !!monitor.isOver(),
        }),
    }));

    return (
        <div 
            ref={drop} 
            className={`board-slot ${isOver ? 'hover' : ''}`}
        >
            {card && <Card card={card} />}
        </div>
    );
};

export default BoardSlot; 