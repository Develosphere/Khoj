import type { TransformKeyframe, Vector3 } from '../types/simulation'

export type ResolvedTransform = { position: Vector3; rotation: Vector3 }

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

export function clampSimulationTime(time: number, duration: number) {
  return Math.min(Math.max(time, 0), duration)
}
