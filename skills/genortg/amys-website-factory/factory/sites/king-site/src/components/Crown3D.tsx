'use client';

import { useEffect, useRef } from 'react';
import * as THREE from 'three';

export default function Crown3D() {
  const mountRef = useRef<HTMLDivElement>(null);
  const crownRef = useRef<THREE.Group>(null);

  useEffect(() => {
    if (!mountRef.current) return;

    const w = mountRef.current.clientWidth;
    const h = mountRef.current.clientHeight;

    // Scene + camera
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 100);
    camera.position.set(0, 1.5, 6);
    camera.lookAt(0, 0, 0);

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(w, h);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    mountRef.current.appendChild(renderer.domElement);

    // Lights
    const ambient = new THREE.AmbientLight(0x444444, 1.5);
    scene.add(ambient);

    const point1 = new THREE.PointLight(0xffd700, 3, 20);
    point1.position.set(3, 4, 3);
    scene.add(point1);

    const point2 = new THREE.PointLight(0xffec80, 2, 15);
    point2.position.set(-3, 2, 2);
    scene.add(point2);

    const point3 = new THREE.PointLight(0xb8860b, 1.5, 10);
    point3.position.set(0, -2, 4);
    scene.add(point3);

    // Crown group
    const crown = new THREE.Group();

    // Base ring (torus)
    const baseGeo = new THREE.TorusGeometry(1.5, 0.15, 16, 64);
    const goldMat = new THREE.MeshStandardMaterial({
      color: 0xffd700,
      metalness: 0.9,
      roughness: 0.15,
      emissive: 0x332200,
      emissiveIntensity: 0.3,
    });
    const base = new THREE.Mesh(baseGeo, goldMat);
    base.rotation.x = Math.PI / 2;
    crown.add(base);

    // Crown body (cylinder)
    const bodyGeo = new THREE.CylinderGeometry(1.5, 1.5, 0.6, 64, 1, true);
    const body = new THREE.Mesh(bodyGeo, goldMat);
    body.position.y = 0.3;
    crown.add(body);

    // Crown top rim
    const topGeo = new THREE.TorusGeometry(1.5, 0.12, 16, 64);
    const top = new THREE.Mesh(topGeo, goldMat);
    top.rotation.x = Math.PI / 2;
    top.position.y = 0.6;
    crown.add(top);

    // Crown spikes (points going up)
    const spikeGeo = new THREE.ConeGeometry(0.12, 0.8, 8);
    const spikeCount = 9;
    for (let i = 0; i < spikeCount; i++) {
      const angle = (i / spikeCount) * Math.PI * 2;
      const x = Math.cos(angle) * 1.5;
      const z = Math.sin(angle) * 1.5;
      const spike = new THREE.Mesh(spikeGeo, goldMat);
      spike.position.set(x, 1.1, z);
      // Point the spike upward
      const dir = new THREE.Vector3(x, 0.6, z).normalize();
      spike.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);
      crown.add(spike);

      // Gem on top of each spike
      const gemGeo = new THREE.SphereGeometry(0.1, 16, 16);
      const gemColors = [0xff0040, 0x0040ff, 0x00ff40, 0xff8000, 0x8000ff];
      const gemMat = new THREE.MeshStandardMaterial({
        color: gemColors[i % gemColors.length],
        metalness: 0.3,
        roughness: 0.1,
        emissive: gemColors[i % gemColors.length],
        emissiveIntensity: 0.5,
      });
      const gem = new THREE.Mesh(gemGeo, gemMat);
      gem.position.set(x, 1.55, z);
      crown.add(gem);
    }

    // Center jewel on top
    const centerGemGeo = new THREE.OctahedronGeometry(0.25, 2);
    const centerGemMat = new THREE.MeshStandardMaterial({
      color: 0xff0040,
      metalness: 0.2,
      roughness: 0.05,
      emissive: 0xff0040,
      emissiveIntensity: 0.8,
    });
    const centerGem = new THREE.Mesh(centerGemGeo, centerGemMat);
    centerGem.position.y = 1.5;
    crown.add(centerGem);

    // Side jewels
    const sideGemGeo = new THREE.OctahedronGeometry(0.12, 1);
    const sideGemMat = new THREE.MeshStandardMaterial({
      color: 0x0040ff,
      metalness: 0.2,
      roughness: 0.05,
      emissive: 0x0040ff,
      emissiveIntensity: 0.6,
    });
    for (let i = 0; i < 3; i++) {
      const angle = (i / 3) * Math.PI * 2 + Math.PI / 6;
      const x = Math.cos(angle) * 1.5;
      const z = Math.sin(angle) * 1.5;
      const gem = new THREE.Mesh(sideGemGeo, sideGemMat);
      gem.position.set(x, 0.6, z);
      crown.add(gem);
    }

    scene.add(crown);
    crownRef.current = crown;

    // Floating particles around crown
    const particleCount = 60;
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.random() * Math.PI;
      const r = 2 + Math.random() * 2;
      positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = r * Math.cos(phi);
      positions[i * 3 + 2] = r * Math.sin(phi) * Math.sin(theta);
    }
    particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const particleMat = new THREE.PointsMaterial({
      color: 0xffd700,
      size: 0.05,
      transparent: true,
      opacity: 0.8,
    });
    const particles = new THREE.Points(particleGeo, particleMat);
    scene.add(particles);

    // Animate
    let animId: number;
    const animate = () => {
      animId = requestAnimationFrame(animate);
      const t = Date.now() * 0.001;

      // Rotate crown
      crown.rotation.y = t * 0.3;
      crown.position.y = Math.sin(t * 0.8) * 0.15;

      // Animate particles
      const pos = particles.geometry.attributes.position.array as Float32Array;
      for (let i = 0; i < particleCount; i++) {
        const idx = i * 3;
        const theta = Math.atan2(pos[idx + 2], pos[idx]);
        const r = Math.sqrt(pos[idx] ** 2 + pos[idx + 2] ** 2);
        const newTheta = theta + 0.005;
        pos[idx] = r * Math.cos(newTheta);
        pos[idx + 2] = r * Math.sin(newTheta);
        pos[idx + 1] += Math.sin(t + i) * 0.002;
      }
      particles.geometry.attributes.position.needsUpdate = true;

      // Animate lights
      point1.position.x = Math.sin(t * 0.5) * 4;
      point1.position.z = Math.cos(t * 0.5) * 4;
      point2.position.x = Math.cos(t * 0.3) * 3;
      point2.position.z = Math.sin(t * 0.3) * 3;

      // Pulse center gem
      const scale = 1 + Math.sin(t * 2) * 0.15;
      centerGem.scale.set(scale, scale, scale);
      centerGem.rotation.y = t * 2;

      renderer.render(scene, camera);
    };
    animate();

    // Resize
    const handleResize = () => {
      const newW = mountRef.current!.clientWidth;
      const newH = mountRef.current!.clientHeight;
      camera.aspect = newW / newH;
      camera.updateProjectionMatrix();
      renderer.setSize(newW, newH);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', handleResize);
      if (mountRef.current && renderer.domElement.parentNode === mountRef.current) {
        mountRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
      // Dispose geometries and materials
      baseGeo.dispose();
      bodyGeo.dispose();
      topGeo.dispose();
      spikeGeo.dispose();

      centerGemGeo.dispose();
      sideGemGeo.dispose();
      particleGeo.dispose();
      goldMat.dispose();

      centerGemMat.dispose();
      sideGemMat.dispose();
      particleMat.dispose();
    };
  }, []);

  return <div ref={mountRef} style={{ width: '100%', height: '100%' }} />;
}
