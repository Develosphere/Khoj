'use client'

import { useMemo } from 'react'
import type { Vehicle } from '../../types/simulation'
import { resolveTransformAtTime } from '../../lib/simulation-runtime'

export default function SimulationVehicle({ vehicle, currentTime }: { vehicle: Vehicle; currentTime: number }) {
  const transform = useMemo(() => resolveTransformAtTime([vehicle.spawn, ...vehicle.motion_track], currentTime), [vehicle, currentTime])
  return <group position={transform.position} rotation={transform.rotation}>
    <mesh castShadow position={[0, 0.48, 0]}><boxGeometry args={[1.55, 0.35, 0.55]} /><meshStandardMaterial color="#f59e0b" metalness={0.35} roughness={0.45} /></mesh>
    <mesh castShadow position={[0.2, 0.75, 0]} rotation={[0, 0, Math.PI / 2]}><cylinderGeometry args={[0.16, 0.16, 1, 16]} /><meshStandardMaterial color="#334155" /></mesh>
    {[-0.6, 0.6].map((x) => <mesh key={x} castShadow position={[x, 0.27, 0]} rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[0.27, 0.27, 0.14, 20]} /><meshStandardMaterial color="#0f172a" /></mesh>)}
  </group>
}
