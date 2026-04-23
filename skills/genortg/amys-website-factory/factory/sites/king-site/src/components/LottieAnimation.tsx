'use client';

import { useEffect, useRef } from 'react';

interface LottieAnimationProps {
  animationUrl?: string;
  loop?: boolean;
  autoplay?: boolean;
}

export default function LottieAnimation({
  animationUrl = 'https://lottie.host/embed/animation',
  loop = true,
  autoplay = true,
}: LottieAnimationProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Create a golden animated ring as fallback (since lottie needs animation data)
    const style = document.createElement('style');
    style.textContent = `
      @keyframes lottieRing {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      @keyframes lottiePulse {
        0%, 100% { opacity: 0.3; transform: scale(0.95); }
        50% { opacity: 0.8; transform: scale(1.05); }
      }
      .lottie-fallback {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
      }
      .lottie-ring {
        width: 120px;
        height: 120px;
        border: 3px solid rgba(255, 215, 0, 0.4);
        border-radius: 50%;
        animation: lottieRing 4s linear infinite;
        position: absolute;
      }
      .lottie-ring:nth-child(2) {
        width: 90px;
        height: 90px;
        border-color: rgba(255, 236, 128, 0.3);
        animation-duration: 3s;
        animation-direction: reverse;
      }
      .lottie-ring:nth-child(3) {
        width: 60px;
        height: 60px;
        border-color: rgba(184, 134, 11, 0.5);
        animation-duration: 5s;
      }
      .lottie-core {
        width: 40px;
        height: 40px;
        background: radial-gradient(circle, #ffd700, #b8860b);
        border-radius: 50%;
        animation: lottiePulse 2s ease-in-out infinite;
        box-shadow: 0 0 30px rgba(255, 215, 0, 0.5);
      }
    `;
    document.head.appendChild(style);

    const wrapper = document.createElement('div');
    wrapper.className = 'lottie-fallback';
    wrapper.innerHTML = `
      <div class="lottie-ring"></div>
      <div class="lottie-ring"></div>
      <div class="lottie-ring"></div>
      <div class="lottie-core"></div>
    `;
    containerRef.current.appendChild(wrapper);

    return () => {
      if (containerRef.current?.firstChild) {
        containerRef.current.removeChild(containerRef.current.firstChild);
      }
      style.remove();
    };
  }, []);

  return (
    <div
      ref={containerRef}
      style={{ width: '100%', height: '100%', position: 'relative' }}
    />
  );
}
