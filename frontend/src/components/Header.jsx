/**
 * =============================================================================
 * Projeto: 01 — Chatbot de Suporte Full-Stack (AfesuTech / DIZZIE)
 * Camada: Camada 4 — Arquitetura de Componentes React
 * Arquivo: frontend/src/components/Header.jsx
 * 
 * Cabeçalho institucional com identidade do projeto (Afesu Veleiros / SENAI-SP),
 * marca da empresa e monitoramento em tempo real do status de conexão da API.
 * =============================================================================
 */

import React from 'react';
import { Sparkles, Radio } from 'lucide-react';

export default function Header({ isApiOnline = false }) {
  return (
    <header className="app-header">
      <div className="brand-wrapper">
        {/* Logotipo / Emblema da Marca */}
        <div className="brand-logo-badge" title="Alaency Moda Feminina & IA">
          <Sparkles size={22} />
        </div>

        {/* Informações Institucionais e Curso */}
        <div className="brand-info">
          <h1>Alaency &bull; Moda Feminina &amp; IA</h1>
          <p>
            Afesu Veleiros / SENAI-SP &bull; <span>Curso de Inteligência Artificial &amp; Voz</span>
          </p>
        </div>
      </div>

      {/* Indicador Visual de Conectividade com a API FastAPI */}
      <div className="status-badge" title={isApiOnline ? 'Backend FastAPI conectado' : 'Backend FastAPI desconectado'}>
        <span className={`status-dot ${isApiOnline ? 'online' : 'offline'}`} />
        <span style={{ color: isApiOnline ? 'var(--status-online)' : 'var(--status-offline)' }}>
          {isApiOnline ? 'API Online' : 'API Offline'}
        </span>
        <Radio size={14} style={{ opacity: 0.6 }} />
      </div>
    </header>
  );
}
