/**
 * =============================================================================
 * Projeto: 01 — Chatbot de Suporte Full-Stack (AfesuTech / Alaency)
 * Arquivo: frontend/src/components/AmbientBackground.jsx
 * 
 * Fundo animado ultra leve e econômico:
 * - 100% puro CSS acelerado por GPU (transform3d e opacity)
 * - Zero consumo contínuo de CPU/JavaScript
 * - Otimizado para economizar bateria em smartphones e notebooks
 * - Pontos luminosos discretos com deriva lenta e pulsante
 * =============================================================================
 */

import React, { memo } from 'react';

// Pontos luminosos com posições, tamanhos, cores e durações dessincronizadas
const PARTICLES = [
  { id: 1, top: '12%', left: '15%', size: 4, color: 'var(--accent-primary)', duration: '11s', delay: '-2s' },
  { id: 2, top: '22%', left: '78%', size: 3, color: 'var(--accent-gold)', duration: '14s', delay: '-5s' },
  { id: 3, top: '48%', left: '8%', size: 3, color: 'var(--accent-secondary)', duration: '13s', delay: '-1s' },
  { id: 4, top: '65%', left: '88%', size: 4, color: 'var(--accent-primary)', duration: '16s', delay: '-8s' },
  { id: 5, top: '82%', left: '25%', size: 3, color: 'var(--accent-gold)', duration: '12s', delay: '-3s' },
  { id: 6, top: '35%', left: '92%', size: 2, color: 'var(--accent-secondary)', duration: '15s', delay: '-7s' },
  { id: 7, top: '88%', left: '70%', size: 3, color: 'var(--accent-primary)', duration: '10s', delay: '-4s' },
  { id: 8, top: '8%', left: '55%', size: 2, color: 'var(--accent-gold)', duration: '17s', delay: '-9s' }
];

function AmbientBackground() {
  return (
    <div className="ambient-background" aria-hidden="true">
      {PARTICLES.map((p) => (
        <span
          key={p.id}
          className="ambient-dot"
          style={{
            top: p.top,
            left: p.left,
            width: `${p.size}px`,
            height: `${p.size}px`,
            backgroundColor: p.color,
            boxShadow: `0 0 ${p.size * 3}px ${p.color}`,
            animationDuration: p.duration,
            animationDelay: p.delay
          }}
        />
      ))}
    </div>
  );
}

// Memoriza o componente para nunca sofrer re-render durante o uso do chat
export default memo(AmbientBackground);
