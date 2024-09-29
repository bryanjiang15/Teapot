import { useDrag } from 'react-dnd'
import Card from './Card' 

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
      <Card card={card}></Card>
    </div>
  )
}