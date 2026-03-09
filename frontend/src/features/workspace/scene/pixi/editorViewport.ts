import * as PIXI from 'pixi.js'
import type { SceneEntity, SceneRoot } from '@/types/scene'

// ─── WorldViewport ────────────────────────────────────────────────────────────

/**
 * Lightweight pan/zoom viewport built on native DOM events.
 * Bypasses pixi-viewport entirely to avoid pixi.js v6/v7 compatibility issues.
 *
 * - Left-click drag to pan (starts after 4px movement threshold)
 * - Scroll wheel to zoom towards cursor
 */
export class WorldViewport {
  readonly container: PIXI.Container

  private canvas: HTMLCanvasElement
  private screenW: number
  private screenH: number

  private panMayStart = false
  private panActive = false
  private panStartX = 0
  private panStartY = 0
  private panLastX = 0
  private panLastY = 0
  private readonly PAN_THRESHOLD = 4

  private readonly _onMouseDown: (e: MouseEvent) => void
  private readonly _onMouseMove: (e: MouseEvent) => void
  private readonly _onMouseUp: (e: MouseEvent) => void
  private readonly _onWheel: (e: WheelEvent) => void
  private readonly _onContextMenu: (e: Event) => void

  constructor(app: PIXI.Application) {
    this.container = new PIXI.Container()
    app.stage.addChild(this.container)

    this.canvas = app.view as HTMLCanvasElement
    this.screenW = app.renderer.width
    this.screenH = app.renderer.height

    this._onMouseDown = (e: MouseEvent) => {
      if (e.button === 0) {
        this.panMayStart = true
        this.panActive = false
        this.panStartX = e.clientX
        this.panStartY = e.clientY
        this.panLastX = e.clientX
        this.panLastY = e.clientY
      }
    }

    this._onMouseMove = (e: MouseEvent) => {
      if (!this.panMayStart) return
      const dx = e.clientX - this.panLastX
      const dy = e.clientY - this.panLastY

      if (!this.panActive) {
        const totalDx = e.clientX - this.panStartX
        const totalDy = e.clientY - this.panStartY
        if (Math.sqrt(totalDx * totalDx + totalDy * totalDy) < this.PAN_THRESHOLD) return
        this.panActive = true
        this.canvas.style.cursor = 'grabbing'
      }

      this.container.x += dx
      this.container.y += dy
      this.panLastX = e.clientX
      this.panLastY = e.clientY
    }

    this._onMouseUp = (e: MouseEvent) => {
      if (e.button === 0) {
        this.panMayStart = false
        this.panActive = false
        this.canvas.style.cursor = 'default'
      }
    }

    this._onWheel = (e: WheelEvent) => {
      e.preventDefault()
      const factor = e.deltaY < 0 ? 1.1 : 1 / 1.1
      const rect = this.canvas.getBoundingClientRect()
      const mx = e.clientX - rect.left
      const my = e.clientY - rect.top

      // Zoom towards mouse cursor position
      const wx = (mx - this.container.x) / this.container.scale.x
      const wy = (my - this.container.y) / this.container.scale.y
      const newScale = Math.max(0.1, Math.min(8, this.container.scale.x * factor))
      this.container.scale.set(newScale)
      this.container.x = mx - wx * newScale
      this.container.y = my - wy * newScale
    }

    this._onContextMenu = (e: Event) => e.preventDefault()

    this.canvas.addEventListener('mousedown', this._onMouseDown)
    window.addEventListener('mousemove', this._onMouseMove)
    window.addEventListener('mouseup', this._onMouseUp)
    this.canvas.addEventListener('wheel', this._onWheel, { passive: false })
    this.canvas.addEventListener('contextmenu', this._onContextMenu)
  }

  addChild(child: PIXI.DisplayObject): PIXI.DisplayObject {
    return this.container.addChild(child)
  }

  moveCenter(worldX: number, worldY: number): void {
    this.container.x = this.screenW / 2 - worldX * this.container.scale.x
    this.container.y = this.screenH / 2 - worldY * this.container.scale.y
  }

  resize(w: number, h: number): void {
    this.screenW = w
    this.screenH = h
  }

  destroy(): void {
    this.canvas.removeEventListener('mousedown', this._onMouseDown)
    window.removeEventListener('mousemove', this._onMouseMove)
    window.removeEventListener('mouseup', this._onMouseUp)
    this.canvas.removeEventListener('wheel', this._onWheel)
    this.canvas.removeEventListener('contextmenu', this._onContextMenu)
  }
}

export function createViewport(app: PIXI.Application): WorldViewport {
  return new WorldViewport(app)
}

// ─── Grid ─────────────────────────────────────────────────────────────────────

/** Draws a grid background into `gfx`, sized to worldWidth×worldHeight. */
export function drawGrid(
  gfx: PIXI.Graphics,
  worldWidth = 4000,
  worldHeight = 4000,
  step = 40,
) {
  gfx.clear()
  // Background fill — warm cream matching the app theme
  gfx.beginFill(0xf5f0e6)
  gfx.drawRect(0, 0, worldWidth, worldHeight)
  gfx.endFill()

  // Fine grid lines
  gfx.lineStyle(1, 0xddd5c4, 0.6)
  for (let x = 0; x <= worldWidth; x += step) {
    gfx.moveTo(x, 0)
    gfx.lineTo(x, worldHeight)
  }
  for (let y = 0; y <= worldHeight; y += step) {
    gfx.moveTo(0, y)
    gfx.lineTo(worldWidth, y)
  }

  // Bold major lines every 5 cells
  gfx.lineStyle(1, 0xc9bfad, 0.8)
  for (let x = 0; x <= worldWidth; x += step * 5) {
    gfx.moveTo(x, 0)
    gfx.lineTo(x, worldHeight)
  }
  for (let y = 0; y <= worldHeight; y += step * 5) {
    gfx.moveTo(0, y)
    gfx.lineTo(worldWidth, y)
  }
}

// ─── Entity building ─────────────────────────────────────────────────────────

/** Pixel dimensions used when drawing entity visual placeholders. */
const ENTITY_WIDTH = 160
const ENTITY_HEIGHT = 80
const ENTITY_PADDING = 10

/** Colours per entity type (fill, border). */
const TYPE_COLORS: Record<string, { fill: number; border: number; alpha: number }> = {
  slot:      { fill: 0xfef9c3, border: 0xd97706, alpha: 0.9 },  // amber — layout region
  component: { fill: 0xdbeafe, border: 0x3b82f6, alpha: 0.95 }, // blue  — sub-component reference
  sprite:    { fill: 0xdcfce7, border: 0x16a34a, alpha: 0.9 },  // green — image placeholder
  text:      { fill: 0xfce7f3, border: 0xdb2777, alpha: 0.9 },  // pink  — text element
}

/** Build a PIXI.Container that visually represents one SceneEntity.
 *  Recurses into children, stacking them below with a small vertical offset.
 */
export function buildEntityContainer(
  entity: SceneEntity,
  onSelect: (id: string) => void,
): PIXI.Container {
  const outer = new PIXI.Container()
  outer.name = entity.id
  outer.position.set(entity.transform.x, entity.transform.y)
  outer.rotation = entity.transform.rotation
  outer.scale.set(entity.transform.scaleX, entity.transform.scaleY)

  const colors = TYPE_COLORS[entity.type] ?? TYPE_COLORS['slot']

  // Background shape
  const gfx = new PIXI.Graphics()
  gfx.beginFill(colors.fill, colors.alpha)
  gfx.lineStyle(2, colors.border, 1)

  if (entity.type === 'slot') {
    // Dashed-style rounded rect — we approximate with a solid rect + distinct color
    gfx.drawRoundedRect(0, 0, ENTITY_WIDTH, ENTITY_HEIGHT, 8)
  } else {
    gfx.drawRoundedRect(0, 0, ENTITY_WIDTH, ENTITY_HEIGHT, 4)
  }
  gfx.endFill()
  outer.addChild(gfx)

  // Label
  const label = new PIXI.Text(
    entity.type === 'slot' && entity.slotKey
      ? `[${entity.slotKey}]\n${entity.name}`
      : entity.name,
    {
      fontSize: 11,
      fill: 0x374151,
      wordWrap: true,
      wordWrapWidth: ENTITY_WIDTH - ENTITY_PADDING * 2,
      align: 'center',
    },
  )
  label.position.set(ENTITY_PADDING, ENTITY_PADDING)
  outer.addChild(label)

  // Type badge (top-right corner)
  const badge = new PIXI.Text(entity.type, {
    fontSize: 9,
    fill: colors.border,
    fontWeight: 'bold',
  })
  badge.position.set(ENTITY_WIDTH - badge.width - ENTITY_PADDING, 4)
  outer.addChild(badge)

  // Click selection — right-click is consumed by viewport drag
  outer.eventMode = 'static'
  outer.cursor = 'pointer'
  outer.on('pointerdown', (e) => {
    if ((e as PIXI.FederatedPointerEvent).button !== 2) {
      e.stopPropagation()
      onSelect(entity.id)
    }
  })

  // Children — stacked with a row-style offset for clarity
  let childX = 0
  for (const child of entity.children) {
    const childContainer = buildEntityContainer(child, onSelect)
    childContainer.position.set(childX, ENTITY_HEIGHT + 30)
    outer.addChild(childContainer)
    childX += ENTITY_WIDTH + 20
  }

  return outer
}

/** Walk the PIXI display tree and find the container whose `name` === entityId. */
export function findContainerById(
  root: PIXI.Container,
  entityId: string,
): PIXI.Container | null {
  if (root.name === entityId) return root
  for (const child of root.children) {
    if (child instanceof PIXI.Container) {
      const found = findContainerById(child, entityId)
      if (found) return found
    }
  }
  return null
}

// ─── Selection highlight ──────────────────────────────────────────────────────

const HIGHLIGHT_COLOR = 0x3b82f6

/**
 * Draws a blue selection outline over `target` by adding/updating a `PIXI.Graphics`
 * named `__selection__` inside it.
 */
export function applySelectionHighlight(target: PIXI.Container): void {
  let gfx = target.getChildByName('__selection__') as PIXI.Graphics | null
  if (!gfx) {
    gfx = new PIXI.Graphics()
    gfx.name = '__selection__'
    target.addChild(gfx)
  }
  gfx.clear()
  gfx.lineStyle(3, HIGHLIGHT_COLOR, 1)
  gfx.drawRoundedRect(-3, -3, ENTITY_WIDTH + 6, ENTITY_HEIGHT + 6, 10)
}

/** Removes the selection highlight from a container. */
export function removeSelectionHighlight(target: PIXI.Container): void {
  const gfx = target.getChildByName('__selection__') as PIXI.Graphics | null
  if (gfx) {
    gfx.clear()
    target.removeChild(gfx)
    gfx.destroy()
  }
}
