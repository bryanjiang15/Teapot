import React, { useState } from 'react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import CardList from '../components/CardList.js';
import BoardSlot from '../components/BoardSlot.js';
import '../css/Game.css';

const Game = () => {
    const [boardCards, setBoardCards] = useState([null, null, null, null]);
    const [hand, setHand] = useState([
        { id: 1, name: "Card 1", power: 5, health: 5, emoticon: "🗡️" },
        { id: 2, name: "Card 2", power: 3, health: 4, emoticon: "🛡️" },
        { id: 3, name: "Card 3", power: 4, health: 3, emoticon: "🔮" },
    ]);

    const handleDrop = (cardIndex, slotIndex) => {
        const newBoardCards = [...boardCards];
        const newHand = [...hand];
        
        newBoardCards[slotIndex] = hand[cardIndex];
        newHand.splice(cardIndex, 1);
        
        setBoardCards(newBoardCards);
        setHand(newHand);
    };

    const handleConfirm = () => {
        // Handle confirmation of the current board state
        console.log('Current board state:', boardCards);
    };

    return (
        <div className="game-container">
            <DndProvider backend={HTML5Backend}>
                <div className="game-board">
                    {boardCards.map((card, index) => (
                        <BoardSlot
                            key={index}
                            card={card}
                            slotIndex={index}
                            onDrop={handleDrop}
                        />
                    ))}
                </div>
                
                <div className="player-hand">
                    <CardList cards={hand} />
                </div>

                <button 
                    className="confirm-button"
                    onClick={handleConfirm}
                >
                    Confirm Action
                </button>
            </DndProvider>
        </div>
    );
};

export default Game;