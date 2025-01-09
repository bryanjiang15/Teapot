import { useDrag } from 'react-dnd'
import Card from './Card.js' 

/**
 * Your Component
 */
export default function Drag({ isDragging, card }) {
  const [{ opacity }, dragRef] = useDrag(
    () => ({
      type: 'card',
      item: { card },
      collect: (monitor) => ({
        opacity: monitor.isDragging() ? 0.5 : 1
      })
    }),
    []
  )

  return (
    <div ref={dragRef} style={{ opacity }}>
      <Card key={1} card={card}></Card>
    </div>
  )
}