/**
 * =============================================================================
 * Projeto: 01 — Chatbot de Suporte Full-Stack (AfesuTech / DIZZIE)
 * Camada: Camada 4 — Arquitetura de Componentes React
 * Arquivo: frontend/src/App.jsx
 * 
 * Componente raiz da aplicação React:
 * - Monitoramento contínuo de integridade da API FastAPI (Health Check /api/metrics)
 * - Orquestração do Header institucional e da janela ChatWindow
 * =============================================================================
 */

import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import ChatWindow from './components/ChatWindow';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function App() {
  const [isApiOnline, setIsApiOnline] = useState(false);

  // Verificação periódica de conectividade com a API (Health Check)
  useEffect(() => {
    let isSubscribed = true;

    const checkApiHealth = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/metrics`, {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        });

        if (isSubscribed) {
          setIsApiOnline(response.ok);
        }
      } catch {
        if (isSubscribed) {
          setIsApiOnline(false);
        }
      }
    };

    // Checagem imediata ao carregar a página
    checkApiHealth();

    // Checagem contínua a cada 10 segundos
    const intervalId = setInterval(checkApiHealth, 10000);

    return () => {
      isSubscribed = false;
      clearInterval(intervalId);
    };
  }, []);

  return (
    <div className="app-root" style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header isApiOnline={isApiOnline} />
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <ChatWindow />
      </main>
    </div>
  );
}
