import { useEffect, useRef } from 'react'
import * as PIXI from 'pixi.js'
import type { SceneRoot, SceneTransform } from '@/types/scene'
import {
  WorldViewport,
  createViewport,
  drawGrid,
  buildEntityContainer,
  findContainerById,
  applySelectionHighlight,
  removeSelectionHighlight,
} from './pixi/editorViewport'

export interface SceneBridge {
  getSceneRoot: () => SceneRoot
  getComponentId: () => string
  getSelectedEntityId: () => string | null
  onSelectEntity: (entityId: string) => void
  onTransformEntity: (entityId: string, patch: { transform?: Partial<SceneTransform> }) => void
}

interface PixiSceneViewProps {
  className?: string
  sceneRoot: SceneRoot
  componentId: string
  selectedEntityId: string | null
  onSelectEntity: (entityId: string) => void
  onTransformEntity: (entityId: string, patch: { transform?: Partial<SceneTransform> }) => void
}

const WORLD_W = 4000
const WORLD_H = 4000

export function PixiSceneView({
  className,
  sceneRoot,
  componentId,
  selectedEntityId,
  onSelectEntity,
  onTransformEntity,
}: PixiSceneViewProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const appRef = useRef<PIXI.Application | null>(null)
  const viewportRef = useRef<WorldViewport | null>(null)
  const entityLayerRef = useRef<PIXI.Container | null>(null)

  // Refs to latest prop values — read inside the ticker without re-running useEffect
  const sceneRootRef = useRef<SceneRoot>(sceneRoot)
  const selectedEntityIdRef = useRef<string | null>(selectedEntityId)
  const onSelectEntityRef = useRef(onSelectEntity)
  const onTransformEntityRef = useRef(onTransformEntity)

  sceneRootRef.current = sceneRoot
  selectedEntityIdRef.current = selectedEntityId
  onSelectEntityRef.current = onSelectEntity
  onTransformEntityRef.current = onTransformEntity

  // Tracks what was last rendered so we only rebuild on changes
  const lastSceneRootRef = useRef<SceneRoot>(null)
  const lastSelectedIdRef = useRef<string | null>(null)

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    let cancelled = false

    const setup = async () => {
      const app = new PIXI.Application({
        resizeTo: container,
        background: 0xf5f0e6,
        antialias: true,
        autoDensity: true,
        resolution: window.devicePixelRatio || 1,
      })

      if (cancelled) {
        app.destroy(true, true)
        return
      }

      container.appendChild(app.view as HTMLCanvasElement)
      appRef.current = app

      // Grid background (static)
      const gridGfx = new PIXI.Graphics()
      drawGrid(gridGfx, WORLD_W, WORLD_H)

      // Viewport with pan + zoom
      const viewport = createViewport(app)
      viewportRef.current = viewport
      viewport.addChild(gridGfx)

      // Entity layer sits on top of the grid
      const entityLayer = new PIXI.Container()
      entityLayerRef.current = entityLayer
      viewport.addChild(entityLayer)

      // Center viewport on the middle of the world
      viewport.moveCenter(WORLD_W / 2, WORLD_H / 2)

      // Ticker: check for state changes and rebuild/reselect as needed
      app.ticker.add(() => {
        const currentRoot = sceneRootRef.current
        const currentSelectedId = selectedEntityIdRef.current

        // Rebuild display list when scene root changes
        if (currentRoot !== lastSceneRootRef.current) {
          lastSceneRootRef.current = currentRoot
          lastSelectedIdRef.current = null // selection highlight will be re-applied below

          // Destroy old children
          entityLayer.removeChildren().forEach((c) => c.destroy({ children: true }))

          if (currentRoot) {
            const rootContainer = buildEntityContainer(
              currentRoot,
              (id) => onSelectEntityRef.current(id),
            )
            // Place tree roughly centred in the world
            rootContainer.position.set(WORLD_W / 2 - 80, WORLD_H / 2 - 40)
            entityLayer.addChild(rootContainer)
          }
        }

        // Apply/move selection highlight when selected entity changes
        if (currentSelectedId !== lastSelectedIdRef.current) {
          // Remove old highlight
          if (lastSelectedIdRef.current) {
            const old = findContainerById(entityLayer, lastSelectedIdRef.current)
            if (old) removeSelectionHighlight(old)
          }
          // Apply new highlight
          if (currentSelectedId) {
            const target = findContainerById(entityLayer, currentSelectedId)
            if (target) applySelectionHighlight(target)
          }
          lastSelectedIdRef.current = currentSelectedId
        }
      })

      // Resize via ResizeObserver
      const ro = new ResizeObserver(() => {
        if (!appRef.current || !viewportRef.current) return
        const { clientWidth: w, clientHeight: h } = container
        appRef.current.renderer.resize(w, h)
        viewportRef.current.resize(w, h)
      })
      ro.observe(container)

      // Store cleanup reference
      ;(app as unknown as { _ro: ResizeObserver })._ro = ro
    }

    setup()

    return () => {
      cancelled = true
      const app = appRef.current
      if (app) {
        ;(app as unknown as { _ro?: ResizeObserver })._ro?.disconnect()
        viewportRef.current?.destroy()
        app.destroy(true, true)
        appRef.current = null
        viewportRef.current = null
        entityLayerRef.current = null
        lastSceneRootRef.current = null
        lastSelectedIdRef.current = null
      }
    }
  }, [])

  return (
    <div
      ref={containerRef}
      className={className}
      style={{ width: '100%', height: '100%', overflow: 'hidden' }}
    />
  )
}
