'use client'

import { Grid } from '@react-three/drei/core/Grid'
import { OrbitControls } from '@react-three/drei/core/OrbitControls'
import type { SimulationScreenplay } from '../../types/simulation'
import SimulationActor from './actor'
import SimulationVehicle from './vehicle'

function EnvironmentScene() {
  return <>
    <color attach="background" args={['#0b1220']} />
    <ambientLight intensity={0.55} />
    <directionalLight castShadow position={[8, 14, 6]} intensity={1.4} shadow-mapSize={[1024, 1024]} />
    <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[100, 100]} /><meshStandardMaterial color="#263445" /></mesh>
    <mesh receiveShadow position={[0, 0.012, 0]} rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[100, 7]} /><meshStandardMaterial color="#111827" /></mesh>
    <Grid args={[100, 100]} cellSize={1} cellThickness={0.35} cellColor="#475569" sectionSize={5} sectionThickness={0.7} sectionColor="#64748b" fadeDistance={45} fadeStrength={1} position={[0, 0.025, 0]} />
    {[-20, -10, 10, 20].map((x) => <group key={x} position={[x, 0, 8]}><mesh castShadow position={[0, 1.5, 0]}><boxGeometry args={[3.5, 3, 2.5]} /><meshStandardMaterial color="#334155" /></mesh><mesh castShadow position={[0, 3.6, 0]}><coneGeometry args={[2.8, 1.5, 4]} /><meshStandardMaterial color="#475569" /></mesh></group>)}
    <OrbitControls makeDefault target={[-4, 0, 0]} maxPolarAngle={Math.PI / 2.1} />
  </>
}

export default function SimulationScene({ screenplay, currentTime }: { screenplay: SimulationScreenplay; currentTime: number }) {
  return <>
    <EnvironmentScene />
    {screenplay.actors.map((actor) => <SimulationActor key={actor.id} actor={actor} currentTime={currentTime} />)}
    {screenplay.vehicles.map((vehicle) => <SimulationVehicle key={vehicle.id} vehicle={vehicle} currentTime={currentTime} />)}
  </>
}
