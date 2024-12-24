import { useDrop } from 'react-dnd';
import Card from './card.js';

export default function DropArea({ onDrop, droppedArr }) {
  const [{ isOver }, dropRef] = useDrop({
    accept: 'card',
    drop: (item) => onDrop(item),
    collect: (monitor) => ({
      isOver: !!monitor.isOver(),
    }),
  });

  return (
    <div
      ref={dropRef}
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
            droppedArr.map((item, index) => (
                <Card key = {item.card.id} card = {item.card}></Card>
            ))
        }
      </div>
    </div>
  );
}