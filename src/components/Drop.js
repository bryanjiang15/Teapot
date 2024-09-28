import { useDrop } from 'react-dnd';

export default function DropArea({ onDrop }) {
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
        height: '200px',
        width: '200px',
        backgroundColor: isOver ? 'lightgreen' : 'lightblue',
        padding: '16px',
      }}
    >
      Drop Here
    </div>
  );
}