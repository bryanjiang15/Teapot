import { useDrop } from 'react-dnd';

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
                <p key={index}>{item}</p>
            ))
        }
      </div>
    </div>
  );
}