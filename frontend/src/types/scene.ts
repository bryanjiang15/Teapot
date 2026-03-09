/** Transform for a scene entity (visual position within the parent template). */
export interface SceneTransform {
  x: number
  y: number
  rotation: number
  scaleX: number
  scaleY: number
}

/**
 * Composition entity types:
 *  - slot:      A named layout region inside this component template (e.g. "artwork", "stats-bar").
 *  - component: A reference to another ProjectComponent embedded here (e.g. a ManaCost inside a Card).
 *  - sprite:    A visual image/asset placeholder.
 *  - text:      A text label.
 */
export type SceneEntityType = 'slot' | 'component' | 'sprite' | 'text'

/** A node in the composition tree. */
export interface SceneEntity {
  id: string
  name: string
  type: SceneEntityType
  transform: SceneTransform
  children: SceneEntity[]
  /**
   * Named key for slot-type entities (e.g. 'artwork', 'stats-bar', 'name').
   * Used as the visual label in the 2D editor and as the data contract key for AI agents.
   */
  slotKey?: string
  /** Image/shape asset reference (for sprite type). */
  assetId?: string
  /**
   * ID of another ProjectComponent this entity references (for component type).
   * Renamed from componentId to avoid confusion with Redux action params.
   */
  componentRef?: string
}

/** Root of a component's composition tree; null means empty composition. */
export type SceneRoot = SceneEntity | null

export const DEFAULT_TRANSFORM: SceneTransform = {
  x: 0,
  y: 0,
  rotation: 0,
  scaleX: 1,
  scaleY: 1,
}
