'use client'

import { useMemo } from 'react'
import type { Vehicle } from '../../types/simulation'
import { resolveActionAtTime, resolveOrientationAtTime, resolveTransformAtTime } from '../../lib/simulation-runtime'
import { resolveVehicleModel } from '../../lib/model-registry'

function Wheel({ x, spin }: { x: number; spin: number }) {
  return <mesh castShadow position={[x, 0.3, 0]} rotation={[Math.PI / 2, spin, 0]}><cylinderGeometry args={[0.3, 0.3, 0.12, 18]} /><meshStandardMaterial color="#111827" roughness={0.7} /></mesh>
}

export default function SimulationVehicle({ vehicle, currentTime }: { vehicle: Vehicle; currentTime: number }) {
  resolveVehicleModel(vehicle.model_key)
  const track = useMemo(() => [vehicle.spawn, ...vehicle.motion_track], [vehicle])
  const transform = useMemo(() => resolveTransformAtTime(track, currentTime), [track, currentTime])
  const orientation = useMemo(() => resolveOrientationAtTime(track, currentTime), [track, currentTime])
  const action = resolveActionAtTime(vehicle.actions, currentTime)
  const driving = action?.type === 'drive'
  const spin = driving ? currentTime * 12 : 0
  return <group position={transform.position} rotation={orientation}>
    <Wheel x={-0.62} spin={spin} /><Wheel x={0.62} spin={spin} />
    <mesh castShadow position={[0, 0.54, 0]}><boxGeometry args={[1.5, 0.24, 0.42]} /><meshStandardMaterial color="#243244" metalness={0.5} roughness={0.4} /></mesh>
    <mesh castShadow position={[-0.1, 0.74, 0]} rotation={[0, 0, Math.PI / 2]}><capsuleGeometry args={[0.2, 0.56, 6, 12]} /><meshStandardMaterial color="#b7791f" metalness={0.35} roughness={0.35} /></mesh>
    <mesh castShadow position={[0.12, 0.73, 0]}><boxGeometry args={[0.56, 0.14, 0.33]} /><meshStandardMaterial color="#151b27" /></mesh>
    <group position={[0.7, 0.66, 0]} rotation={[0, 0, -0.35]}><mesh castShadow><cylinderGeometry args={[0.055, 0.055, 0.75, 10]} /><meshStandardMaterial color="#94a3b8" metalness={0.7} /></mesh><mesh castShadow position={[0, 0.35, 0]} rotation={[0, 0, Math.PI / 2]}><cylinderGeometry args={[0.04, 0.04, 0.65, 10]} /><meshStandardMaterial color="#94a3b8" /></mesh></group>
  </group>
}
