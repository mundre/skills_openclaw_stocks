"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import {
  VRM,
  VRMUtils,
  VRMLoaderPlugin,
} from "@pixiv/three-vrm";

type Emotion = "neutral" | "happy" | "sad" | "angry" | "surprised";

type AvatarStageProps = {
  modelFile: File | null;
  emotion: Emotion;
  mouthOpen: number;
  pose?: number;
};

const expressionMap: Record<Emotion, Record<string, number>> = {
  neutral: {},
  happy: { happy: 0.95, relaxed: 0.35 },
  sad: { sad: 0.9, relaxed: 0.2 },
  angry: { angry: 0.95, relaxed: 0.1 },
  surprised: { surprised: 0.95, aa: 0.75, oh: 0.5 },
};

function applyExpression(vrm: VRM, emotion: Emotion, mouthOpen: number) {
  const manager = vrm.expressionManager as unknown as {
    setValue?: (name: string, value: number) => void;
    resetValues?: () => void;
  } | null;

  if (!manager?.setValue) return;

  manager.resetValues?.();
  const values = expressionMap[emotion];
  for (const [key, value] of Object.entries(values)) {
    manager.setValue(key, value);
  }

  const open = Math.max(0, Math.min(1, mouthOpen));
  manager.setValue("aa", Math.max(open, values.aa ?? 0));
  manager.setValue("ih", open * 0.4);
  manager.setValue("ou", open * 0.2);
  manager.setValue("ee", open * 0.1);
  manager.setValue("oh", open * 0.25);
}

export function AvatarStage({
  modelFile,
  emotion,
  mouthOpen,
  pose = 0,
}: AvatarStageProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [status, setStatus] = useState("No model loaded");
  const vrmRef = useRef<VRM | null>(null);
  const modelUrl = useMemo(
    () => (modelFile ? URL.createObjectURL(modelFile) : ""),
    [modelFile]
  );

  useEffect(() => {
    if (!canvasRef.current) return;

    const canvas = canvasRef.current;
    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#090814");

    const camera = new THREE.PerspectiveCamera(
      35,
      canvas.clientWidth / canvas.clientHeight,
      0.1,
      100
    );
    camera.position.set(0, 1.42, 3.6);

    const renderer = new THREE.WebGLRenderer({
      canvas,
      alpha: true,
      antialias: true,
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(canvas.clientWidth, canvas.clientHeight, false);
    renderer.outputColorSpace = THREE.SRGBColorSpace;

    const hemi = new THREE.HemisphereLight(0xffffff, 0x2a1740, 2.3);
    scene.add(hemi);

    const key = new THREE.DirectionalLight(0xffd6fb, 3.1);
    key.position.set(2, 5, 3);
    scene.add(key);

    const fill = new THREE.DirectionalLight(0x8ffcff, 1.5);
    fill.position.set(-2, 2, 2);
    scene.add(fill);

    const rim = new THREE.PointLight(0xa58bff, 2.2, 20);
    rim.position.set(0, 3, -2);
    scene.add(rim);

    const floor = new THREE.Mesh(
      new THREE.CircleGeometry(6, 64),
      new THREE.MeshStandardMaterial({
        color: 0x140f22,
        roughness: 1,
        metalness: 0,
        transparent: true,
        opacity: 0.95,
      })
    );
    floor.rotation.x = -Math.PI / 2;
    floor.position.y = -1.05;
    scene.add(floor);

    const controls = new OrbitControls(camera, canvas);
    controls.enableDamping = true;
    controls.enablePan = false;
    controls.minDistance = 2.2;
    controls.maxDistance = 6.2;
    controls.target.set(0, 1.3, 0);

    const loader = new GLTFLoader();
    loader.register((parser) => new VRMLoaderPlugin(parser));

    let cancelled = false;
    let animationId = 0;
    let lastTime = performance.now();

    const resize = () => {
      const { clientWidth, clientHeight } = canvas;
      if (!clientWidth || !clientHeight) return;
      camera.aspect = clientWidth / clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(clientWidth, clientHeight, false);
    };

    const onResize = () => resize();
    window.addEventListener("resize", onResize);

    const loadModel = async () => {
      if (!modelUrl) {
        vrmRef.current = null;
        setStatus("Upload a .vrm to wake the avatar");
        return;
      }

      try {
        setStatus("Loading VRM...");
        const gltf = await loader.loadAsync(modelUrl);
        if (cancelled) return;

        const vrm = (gltf.userData.vrm ?? null) as VRM | null;
        if (!vrm) {
          setStatus("That file is not a VRM model");
          return;
        }

        VRMUtils.removeUnnecessaryVertices(gltf.scene);
        VRMUtils.removeUnnecessaryJoints(gltf.scene);

        if (vrmRef.current) {
          scene.remove(vrmRef.current.scene);
        }

        vrm.scene.position.set(0, -1.1, 0);
        vrm.scene.rotation.y = Math.PI;
        scene.add(vrm.scene);
        vrmRef.current = vrm;
        setStatus("Model ready");
      } catch (error) {
        console.error(error);
        setStatus("Could not load VRM");
      }
    };

    void loadModel();
    resize();

    const tick = () => {
      const now = performance.now();
      const delta = Math.min(0.033, (now - lastTime) / 1000);
      lastTime = now;

      const vrm = vrmRef.current;
      if (vrm) {
        applyExpression(vrm, emotion, mouthOpen);
        vrm.scene.rotation.y = Math.PI + Math.sin(now / 3200) * 0.14 + pose * 0.2;
        vrm.update(delta);
      }

      controls.update();
      renderer.render(scene, camera);
      animationId = window.requestAnimationFrame(tick);
    };

    animationId = window.requestAnimationFrame(tick);

    return () => {
      cancelled = true;
      window.cancelAnimationFrame(animationId);
      window.removeEventListener("resize", onResize);
      controls.dispose();
      renderer.dispose();
      if (modelUrl) URL.revokeObjectURL(modelUrl);
      if (vrmRef.current) {
        scene.remove(vrmRef.current.scene);
        vrmRef.current = null;
      }
    };
  }, [modelUrl, emotion, mouthOpen, pose]);

  return (
    <div className="relative h-full min-h-[420px] overflow-hidden rounded-[28px] border border-white/10 bg-[#080714] shadow-[var(--shadow)]">
      <div className="absolute inset-0 grid-noise opacity-40" />
      <canvas ref={canvasRef} className="relative h-full w-full" />
      <div className="absolute left-4 top-4 rounded-full border border-white/10 bg-black/40 px-3 py-1 text-xs text-[var(--muted)] backdrop-blur">
        {status}
      </div>
      <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between gap-3 rounded-2xl border border-white/10 bg-black/45 px-4 py-3 text-xs text-[var(--muted)] backdrop-blur">
        <span>VRM viewport</span>
        <span>{emotion} • mouth {Math.round(mouthOpen * 100)}%</span>
      </div>
    </div>
  );
}
