'use client'

import type { Environment, EnvironmentPreset } from '../../types/simulation'

const palette = {
  day: { background: '#b9c8d1', ground: '#9ca8a8', ambient: 1.1, sun: 1.8, sunColor: '#fff3d1', position: [14, 20, 8] as [number, number, number], fog: '#b9c8d1' },
  dusk: { background: '#29354a', ground: '#526069', ambient: 0.62, sun: 1.1, sunColor: '#efab76', position: [4, 9, 7] as [number, number, number], fog: '#29354a' },
  night: { background: '#0d1624', ground: '#1c2732', ambient: 0.3, sun: 0.35, sunColor: '#9bb9df', position: [2, 9, 5] as [number, number, number], fog: '#0d1624' },
}

function BuildingBlock({ position, width = 4, height = 5, depth = 3, tone = '#53616b' }: { position: [number, number, number]; width?: number; height?: number; depth?: number; tone?: string }) {
  return <group position={position}><mesh castShadow receiveShadow position={[0, height / 2, 0]}><boxGeometry args={[width, height, depth]} /><meshStandardMaterial color={tone} roughness={0.9} /></mesh><mesh position={[0, height * 0.58, depth / 2 + 0.01]}><boxGeometry args={[width * 0.58, height * 0.2, 0.025]} /><meshStandardMaterial color="#9fb2be" emissive="#52616a" emissiveIntensity={0.18} /></mesh></group>
}

function StreetLight({ position }: { position: [number, number, number] }) {
  return <group position={position}><mesh castShadow position={[0, 2.5, 0]}><cylinderGeometry args={[0.045, 0.07, 5, 8]} /><meshStandardMaterial color="#3b4650" metalness={0.55} /></mesh><mesh position={[0, 5.02, 0]}><sphereGeometry args={[0.12, 10, 10]} /><meshStandardMaterial color="#f4d9a6" emissive="#f4c572" emissiveIntensity={1.5} /></mesh><pointLight color="#f4c572" intensity={0.55} distance={8} position={[0, 5, 0]} /></group>
}

function Road({ intersection = false }: { intersection?: boolean }) {
  return <><mesh receiveShadow position={[0, 0.01, 0]} rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[80, 7]} /><meshStandardMaterial color="#283039" roughness={0.96} /></mesh>{intersection && <mesh receiveShadow position={[0, 0.012, 0]} rotation={[-Math.PI / 2, 0, Math.PI / 2]}><planeGeometry args={[80, 7]} /><meshStandardMaterial color="#283039" roughness={0.96} /></mesh>} {[-28, -14, 0, 14, 28].map((x) => <mesh key={x} position={[x, 0.025, 0]} rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[5, 0.1]} /><meshBasicMaterial color="#c9b67b" /></mesh>)}</>
}

function Street({ residential = false, intersection = false }: { residential?: boolean; intersection?: boolean }) {
  const buildingTone = residential ? '#647078' : '#46535d'
  return <><Road intersection={intersection} /><mesh receiveShadow position={[0, 0.015, 4.5]} rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[80, 2]} /><meshStandardMaterial color="#9aa2a0" roughness={0.95} /></mesh><mesh receiveShadow position={[0, 0.015, -4.5]} rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[80, 2]} /><meshStandardMaterial color="#9aa2a0" roughness={0.95} /></mesh>{[-28, -18, -8, 7, 18, 29].map((x, index) => <BuildingBlock key={x} position={[x, 0, index % 2 ? 8 : -8]} width={residential ? 5 : 6} height={residential ? 3.5 : 5 + (index % 3)} depth={residential ? 4 : 5} tone={buildingTone} />)} {[-25, -10, 5, 20].map((x) => <StreetLight key={x} position={[x, 0, 3.7]} />)}</>
}

function Interior({ preset }: { preset: EnvironmentPreset }) {
  if (preset === 'corridor') return <><mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[36, 5]} /><meshStandardMaterial color="#4f5960" /></mesh>{[-2.5, 2.5].map((z) => <mesh key={z} position={[0, 2, z]}><boxGeometry args={[36, 4, 0.12]} /><meshStandardMaterial color="#74808a" /></mesh>)}{[-12, 0, 12].map((x) => <pointLight key={x} position={[x, 3.5, 0]} intensity={0.7} distance={7} color="#e8e3cf" />)}</>
  return <><mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[24, 18]} /><meshStandardMaterial color="#797a72" roughness={0.9} /></mesh><BuildingBlock position={[-6, 0, 0]} width={0.2} height={4} depth={18} tone="#65717a" /><BuildingBlock position={[6, 0, 0]} width={0.2} height={4} depth={18} tone="#65717a" /><mesh castShadow position={[0, 0.8, 0]}><boxGeometry args={[4, 1.4, 2]} /><meshStandardMaterial color="#4f5c62" /></mesh><pointLight position={[0, 3.5, 0]} intensity={0.9} distance={10} color="#f3e6c7" /></>
}

function ParkingArea() { return <><mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[60, 36]} /><meshStandardMaterial color="#384149" /></mesh>{[-15, -5, 5, 15].map((x) => <mesh key={x} position={[x, 0.02, 0]} rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[0.12, 28]} /><meshBasicMaterial color="#b9b8a5" /></mesh>)}<BuildingBlock position={[0, 0, 14]} width={24} height={5} depth={4} tone="#56636b" /></> }

function Exterior() { return <><mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[48, 32]} /><meshStandardMaterial color="#89918e" /></mesh><BuildingBlock position={[0, 0, 5]} width={18} height={8} depth={2} tone="#4d5a64" /><mesh position={[0, 1.4, 3.95]}><boxGeometry args={[3, 2.8, 0.08]} /><meshStandardMaterial color="#202a32" /></mesh><StreetLight position={[-8, 0, -3]} /><StreetLight position={[8, 0, -3]} /></> }

export default function EnvironmentScene({ environment }: { environment: Environment }) {
  const safePreset: EnvironmentPreset = ['urban_street', 'residential_street', 'intersection', 'building_exterior', 'office_room', 'parking_area', 'corridor'].includes(environment.preset) ? environment.preset : 'urban_street'
  const lighting = palette[environment.time_of_day] ?? palette.day
  const fogDensity = environment.weather?.toLowerCase().includes('fog') ? 0.035 : environment.time_of_day === 'night' ? 0.012 : 0.004
  return <><color attach="background" args={[lighting.background]} /><fog attach="fog" args={[lighting.fog, 20, fogDensity > 0.02 ? 65 : 110]} /><hemisphereLight intensity={lighting.ambient} color="#dbe8ed" groundColor="#27313a" /><directionalLight castShadow position={lighting.position} intensity={lighting.sun} color={lighting.sunColor} shadow-mapSize={[1024, 1024]} shadow-camera-far={45} />
    {safePreset === 'urban_street' && <Street />}{safePreset === 'residential_street' && <Street residential />}{safePreset === 'intersection' && <Street intersection />}{safePreset === 'building_exterior' && <Exterior />}{safePreset === 'office_room' && <Interior preset="office_room" />}{safePreset === 'parking_area' && <ParkingArea />}{safePreset === 'corridor' && <Interior preset="corridor" />}
  </>
}
