'use client';

import { useRef, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Grid, Environment, Float } from '@react-three/drei';
import * as THREE from 'three';

interface Mesh3DViewerProps {
    numElements?: number;
    elementType?: string;
    qualityScore?: number;
}

function MeshGeometry({ numElements = 5000, qualityScore = 90 }: { numElements: number; qualityScore: number }) {
    const meshRef = useRef<THREE.Mesh>(null);

    useFrame((state) => {
        if (meshRef.current) {
            meshRef.current.rotation.y = state.clock.elapsedTime * 0.1;
        }
    });

    // Generate vertices based on numElements
    const detail = Math.min(Math.floor(numElements / 500), 20);

    // Color based on quality score
    const color = qualityScore > 80
        ? '#10b981'
        : qualityScore > 60
            ? '#f59e0b'
            : '#ef4444';

    return (
        <Float speed={1} rotationIntensity={0.2} floatIntensity={0.5}>
            <mesh ref={meshRef}>
                <icosahedronGeometry args={[1.5, detail]} />
                <meshStandardMaterial
                    color={color}
                    wireframe
                    transparent
                    opacity={0.8}
                />
            </mesh>
            {/* Solid inner mesh */}
            <mesh ref={meshRef}>
                <icosahedronGeometry args={[1.45, detail]} />
                <meshStandardMaterial
                    color={color}
                    transparent
                    opacity={0.2}
                />
            </mesh>
        </Float>
    );
}

function Scene({ numElements, qualityScore }: { numElements: number; qualityScore: number }) {
    return (
        <>
            <ambientLight intensity={0.4} />
            <directionalLight position={[10, 10, 5]} intensity={1} />
            <pointLight position={[-10, -10, -10]} color="#3b82f6" intensity={0.5} />
            <MeshGeometry numElements={numElements} qualityScore={qualityScore} />
            <Grid
                args={[10, 10]}
                cellSize={0.5}
                cellThickness={0.5}
                cellColor="#1e40af"
                sectionSize={2}
                sectionThickness={1}
                sectionColor="#3b82f6"
                fadeDistance={25}
                fadeStrength={1}
                followCamera={false}
                infiniteGrid
                position={[0, -2, 0]}
            />
            <OrbitControls
                enablePan={true}
                enableZoom={true}
                enableRotate={true}
                autoRotate={false}
                autoRotateSpeed={0.5}
            />
            <Environment preset="city" />
        </>
    );
}

function LoadingPlaceholder() {
    return (
        <div style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexDirection: 'column',
            gap: '16px',
        }}>
            <div className="spinner" style={{ width: 40, height: 40 }} />
            <span style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
                Loading 3D View...
            </span>
        </div>
    );
}

export function Mesh3DViewer({ numElements = 5000, qualityScore = 90 }: Mesh3DViewerProps) {
    return (
        <div className="viz-container" style={{ background: 'var(--bg-primary)' }}>
            <Suspense fallback={<LoadingPlaceholder />}>
                <Canvas camera={{ position: [3, 3, 3], fov: 50 }}>
                    <Scene numElements={numElements} qualityScore={qualityScore} />
                </Canvas>
            </Suspense>

            {/* Stats overlay */}
            <div style={{
                position: 'absolute',
                bottom: '16px',
                left: '16px',
                background: 'rgba(0,0,0,0.7)',
                padding: '12px 16px',
                borderRadius: 'var(--radius-md)',
                fontSize: '12px',
            }}>
                <div style={{ color: 'var(--text-muted)', marginBottom: '4px' }}>Mesh Statistics</div>
                <div style={{ display: 'flex', gap: '24px' }}>
                    <div>
                        <span style={{ color: 'var(--text-muted)' }}>Elements: </span>
                        <span style={{ color: 'var(--accent-blue)', fontWeight: 600 }}>
                            {numElements.toLocaleString()}
                        </span>
                    </div>
                    <div>
                        <span style={{ color: 'var(--text-muted)' }}>Quality: </span>
                        <span style={{
                            color: qualityScore > 80 ? 'var(--accent-green)' : 'var(--accent-orange)',
                            fontWeight: 600
                        }}>
                            {qualityScore}%
                        </span>
                    </div>
                </div>
            </div>

            {/* Controls hint */}
            <div style={{
                position: 'absolute',
                bottom: '16px',
                right: '16px',
                background: 'rgba(0,0,0,0.7)',
                padding: '8px 12px',
                borderRadius: 'var(--radius-md)',
                fontSize: '11px',
                color: 'var(--text-muted)',
            }}>
                🖱️ Drag to rotate • Scroll to zoom
            </div>
        </div>
    );
}
