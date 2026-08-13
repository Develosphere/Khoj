import type { ActorAction, SimulationEvent, TransformKeyframe, Vector3, VehicleAction } from '../types/simulation'

export type ResolvedTransform = { position: Vector3; rotation: Vector3 }
export type ResolvedAction<T extends ActorAction | VehicleAction> = T & { progress: number }

const lerp = (a: number, b: number, t: number) => a + (b - a) * t
const lerpVector = (a: Vector3, b: Vector3, t: number): Vector3 => [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)]
const rotationOf = (keyframe: TransformKeyframe): Vector3 => keyframe.rotation ?? [0, 0, 0]

export function resolveTransformAtTime(track: TransformKeyframe[], currentTime: number): ResolvedTransform {
  const ordered = [...track].sort((a, b) => a.time - b.time)
  if (ordered.length === 0) return { position: [0, 0, 0], rotation: [0, 0, 0] }
  if (currentTime <= ordered[0].time) return { position: [...ordered[0].position], rotation: [...rotationOf(ordered[0])] }
  const last = ordered[ordered.length - 1]
  if (currentTime >= last.time) return { position: [...last.position], rotation: [...rotationOf(last)] }
  const nextIndex = ordered.findIndex((frame) => frame.time >= currentTime)
  const before = ordered[nextIndex - 1]
  const after = ordered[nextIndex]
  const progress = (currentTime - before.time) / (after.time - before.time)
  return { position: lerpVector(before.position, after.position, progress), rotation: lerpVector(rotationOf(before), rotationOf(after), progress) }
}

export function resolveOrientationAtTime(track: TransformKeyframe[], currentTime: number): Vector3 {
  const ordered = [...track].sort((a, b) => a.time - b.time)
  const explicit = [...ordered].reverse().find((frame) => frame.time <= currentTime && frame.rotation)?.rotation
  if (explicit) return [...explicit]
  if (ordered.length < 2) return [0, 0, 0]
  const index = Math.max(1, ordered.findIndex((frame) => frame.time >= currentTime))
  const segmentIndexes = Array.from({ length: ordered.length - 1 }, (_, offset) => Math.max(0, Math.min(ordered.length - 2, index - 1 - offset)))
  for (const segmentIndex of segmentIndexes) {
    const before = ordered[segmentIndex]
    const after = ordered[segmentIndex + 1]
    const dx = after.position[0] - before.position[0]
    const dz = after.position[2] - before.position[2]
    if (Math.hypot(dx, dz) >= 0.001) return [0, Math.atan2(dx, dz), 0]
  }
  return [0, 0, 0]
}

export function resolveActionAtTime<T extends ActorAction | VehicleAction>(actions: T[], currentTime: number): ResolvedAction<T> | null {
  const ordered = [...actions].sort((a, b) => a.start - b.start)
  const active = [...ordered].reverse().find((action) => currentTime >= action.start && currentTime <= (action.end ?? Number.POSITIVE_INFINITY))
  if (!active) return null
  const end = active.end ?? active.start
  return { ...active, progress: end === active.start ? 1 : Math.min(1, Math.max(0, (currentTime - active.start) / (end - active.start))) }
}

export const getActiveEvents = (events: SimulationEvent[], currentTime: number) => events.filter((event) => currentTime >= event.time && currentTime <= event.time + (event.duration ?? 0.5))
export const isInferredEvent = (event: SimulationEvent) => event.certainty === 'inferred'

export function clampSimulationTime(time: number, duration: number) {
  return Math.min(Math.max(time, 0), duration)
}
