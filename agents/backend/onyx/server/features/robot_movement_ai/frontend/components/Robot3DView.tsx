'use client';

import { useEffect, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Grid } from '@react-three/drei';
import { useRobotStore } from '@/lib/store/robotStore';
import * as THREE from 'three';

function RobotArm({ position }: { position: [number, number, number] }) {
  const meshRef = useRef<THREE.Group>(null);

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.position.set(...position);
    }
  });

  return (
    <group ref={meshRef} position={position}>
      {/* Base */}
      <mesh position={[0, 0.05, 0]}>
        <boxGeometry args={[0.2, 0.1, 0.2]} />
        <meshStandardMaterial color="#0ea5e9" />
      </mesh>
      {/* Link 1 */}
      <mesh position={[0, 0.25, 0]}>
        <boxGeometry args={[0.05, 0.3, 0.05]} />
        <meshStandardMaterial color="#0284c7" />
      </mesh>
      {/* Joint 1 */}
      <mesh position={[0, 0.4, 0]}>
        <sphereGeometry args={[0.06]} />
        <meshStandardMaterial color="#0369a1" />
      </mesh>
      {/* Link 2 */}
      <mesh position={[0.15, 0.4, 0]}>
        <boxGeometry args={[0.3, 0.05, 0.05]} />
        <meshStandardMaterial color="#0284c7" />
      </mesh>
      {/* Joint 2 */}
      <mesh position={[0.3, 0.4, 0]}>
        <sphereGeometry args={[0.06]} />
        <meshStandardMaterial color="#0369a1" />
      </mesh>
      {/* End Effector */}
      <mesh position={[0.3, 0.4, 0]}>
        <boxGeometry args={[0.08, 0.08, 0.08]} />
        <meshStandardMaterial color="#10b981" emissive="#10b981" emissiveIntensity={0.5} />
      </mesh>
    </group>
  );
}

function TrajectoryPath({ waypoints }: { waypoints: [number, number, number][] }) {
  if (waypoints.length < 2) return null;

  const points = waypoints.map((wp) => new THREE.Vector3(...wp));
  const geometry = new THREE.BufferGeometry().setFromPoints(points);

  return (
    <line geometry={geometry}>
      <lineBasicMaterial color="#f59e0b" />
    </line>
  );
}

function Obstacle({ bounds }: { bounds: number[] }) {
  const [minX, minY, minZ, maxX, maxY, maxZ] = bounds;
  const center: [number, number, number] = [
    (minX + maxX) / 2,
    (minY + maxY) / 2,
    (minZ + maxZ) / 2,
  ];
  const size: [number, number, number] = [
    maxX - minX,
    maxY - minY,
    maxZ - minZ,
  ];

  return (
    <mesh position={center}>
      <boxGeometry args={size} />
      <meshStandardMaterial color="#ef4444" opacity={0.5} transparent />
    </mesh>
  );
}

export default function Robot3DView({ fullscreen = false }: { fullscreen?: boolean }) {
  const { status, currentPosition, targetPosition } = useRobotStore();
  const [obstacles, setObstacles] = useState<number[][]>([]);
  const [trajectory, setTrajectory] = useState<[number, number, number][]>([]);

  const currentPos: [number, number, number] = currentPosition
    ? [currentPosition.x, currentPosition.y, currentPosition.z]
    : [0, 0, 0];

  const targetPos: [number, number, number] | null = targetPosition
    ? [targetPosition.x, targetPosition.y, targetPosition.z]
    : null;

  // Generate trajectory line if we have both positions
  useEffect(() => {
    if (currentPosition && targetPosition) {
      // Simple linear interpolation for visualization
      const steps = 20;
      const path: [number, number, number][] = [];
      for (let i = 0; i <= steps; i++) {
        const t = i / steps;
        path.push([
          currentPosition.x + (targetPosition.x - currentPosition.x) * t,
          currentPosition.y + (targetPosition.y - currentPosition.y) * t,
          currentPosition.z + (targetPosition.z - currentPosition.z) * t,
        ]);
      }
      setTrajectory(path);
    }
  }, [currentPosition, targetPosition]);

  return (
    <div className={`w-full ${fullscreen ? 'h-screen' : 'h-[500px]'} bg-gray-900 rounded-lg overflow-hidden border border-gray-700`}>
      <Canvas camera={{ position: [2, 2, 2], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <pointLight position={[-10, -10, -5]} intensity={0.5} />

        <Grid args={[10, 10]} cellColor="#374151" sectionColor="#1f2937" />

        {/* Robot Arm */}
        <RobotArm position={currentPos} />

        {/* Target Position */}
        {targetPos && (
          <mesh position={targetPos}>
            <sphereGeometry args={[0.05]} />
            <meshStandardMaterial color="#f59e0b" emissive="#f59e0b" emissiveIntensity={1} />
          </mesh>
        )}

        {/* Trajectory Path */}
        {trajectory.length > 0 && <TrajectoryPath waypoints={trajectory} />}

        {/* Obstacles */}
        {obstacles.map((obs, i) => (
          <Obstacle key={i} bounds={obs} />
        ))}

        <OrbitControls enableDamping dampingFactor={0.05} />
        <axesHelper args={[1]} />
      </Canvas>

      {/* Info Overlay */}
      <div className="absolute top-4 left-4 bg-gray-800/90 backdrop-blur-sm p-3 rounded-lg border border-gray-700 text-white text-sm">
        <div className="space-y-1">
          <div>
            <span className="text-gray-400">Posición Actual: </span>
            <span className="font-mono">
              ({currentPos[0].toFixed(2)}, {currentPos[1].toFixed(2)}, {currentPos[2].toFixed(2)})
            </span>
          </div>
          {targetPos && (
            <div>
              <span className="text-gray-400">Objetivo: </span>
              <span className="font-mono text-yellow-400">
                ({targetPos[0].toFixed(2)}, {targetPos[1].toFixed(2)}, {targetPos[2].toFixed(2)})
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

