/**
 * =============================================================================
 * Projeto: 01 — Chatbot de Suporte Full-Stack (AfesuTech / Alaency)
 * Arquivo: frontend/src/components/AmbientBackground.jsx
 * 
 * Fundo animado claro, sofisticado e ultra leve:
 * - Pontos discretos em Rosa, Verde-Esmeralda e Dourado
 * - 100% puro CSS acelerado por GPU (translate3d e opacity)
 * - Economia total de bateria em celulares e notebooks
 * =============================================================================
 */

import React, { memo } from 'react';

// Poucos pontos luminosos discretos distribuídos de forma equilibrada
const PARTICLES = [
  { id: 1, top: '14%', left: '12%', size: 3.5, color: 'var(--accent-pink)', duration: '12s', delay: '-1s' },
  { id: 2, top: '24%', left: '84%', size: 3, color: 'var(--accent-gold)', duration: '15s', delay: '-6s' },
  { id: 3, top: '46%', left: '6%', size: 3, color: 'var(--accent-emerald)', duration: '13s', delay: '-3s' },
  { id: 4, top: '68%', left: '92%', size: 3.5, color: 'var(--accent-pink)', duration: '16s', delay: '-8s' },
  { id: 5, top: '80%', left: '22%', size: 3, color: 'var(--accent-gold)', duration: '11s', delay: '-4s' },
  { id: 6, top: '38%', left: '94%', size: 2.5, color: 'var(--accent-emerald)', duration: '14s', delay: '-7s' },
  { id: 7, top: '86%', left: '74%', size: 3, color: 'var(--accent-pink)', duration: '13s', delay: '-2s' },
  { id: 8, top: '10%', left: '62%', size: 2.5, color: 'var(--accent-gold)', duration: '17s', delay: '-9s' }
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

export default memo(AmbientBackground);
