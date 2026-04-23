"use client";

import { useMemo, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Float, Points, PointMaterial } from "@react-three/drei";
import type { Group } from "three";

function OrbitShape() {
  const meshRef = useRef<Group>(null);
  const points = useMemo(() => {
    const count = 350;
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      arr[i * 3] = (Math.random() - 0.5) * 8;
      arr[i * 3 + 1] = (Math.random() - 0.5) * 8;
      arr[i * 3 + 2] = (Math.random() - 0.5) * 8;
    }
    return arr;
  }, []);

  useFrame((state) => {
    if (!meshRef.current) return;
    meshRef.current.rotation.x = state.clock.elapsedTime * 0.12;
    meshRef.current.rotation.y = state.clock.elapsedTime * 0.2;
  });

  return (
    <group ref={meshRef}>
      <Float speed={1.4} floatIntensity={1.1}>
        <mesh>
          <icosahedronGeometry args={[1.35, 1]} />
          <meshStandardMaterial wireframe color="#77ffcc" emissive="#6ee7b7" />
        </mesh>
      </Float>
      <mesh scale={0.75}>
        <sphereGeometry args={[1, 32, 32]} />
        <meshBasicMaterial color="#a78bfa" transparent opacity={0.2} />
      </mesh>
      <Points positions={points}>
        <PointMaterial color="#8b5cf6" transparent opacity={0.6} size={0.03} />
      </Points>
    </group>
  );
}

export default function ThreeHero() {
  return (
    <div className="h-full w-full rounded-2xl border border-white/10 shadow-2xl" role="img" aria-label="3D animated hero">
      <Canvas camera={{ position: [0, 0, 4], fov: 55 }}>
        <ambientLight intensity={0.45} />
        <directionalLight position={[2, 2, 3]} intensity={0.9} />
        <pointLight position={[-2, -2, -2]} color="#ff4dd8" intensity={0.8} />
        <OrbitShape />
      </Canvas>
    </div>
  );
}