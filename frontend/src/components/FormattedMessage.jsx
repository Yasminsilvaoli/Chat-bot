/**
 * =============================================================================
 * Projeto: 01 — Chatbot de Suporte Full-Stack (AfesuTech / DIZZIE)
 * Camada: Camada 4 — Interface & Formatação de Respostas
 * Arquivo: frontend/src/components/FormattedMessage.jsx
 * 
 * Componente responsável por converter respostas com sintaxe Markdown
 * (negritos, listas, links, quebras de linha e blocos de código) em HTML renderizável.
 * =============================================================================
 */

import React, { useMemo } from 'react';
import { marked } from 'marked';

// Configurações do compilador de Markdown
marked.setOptions({
  breaks: true, // Converte quebras de linha simples em <br>
  gfm: true,    // GitHub Flavored Markdown (tabelas, listas com caixas, etc.)
});

export default function FormattedMessage({ content }) {
  // Converte a string Markdown para HTML memorizando o resultado
  const htmlContent = useMemo(() => {
    if (!content || typeof content !== 'string') {
      return '';
    }

    try {
      return marked.parse(content);
    } catch (err) {
      console.error('[FormattedMessage] Erro ao processar Markdown:', err);
      return content;
    }
  }, [content]);

  if (!content) {
    return null;
  }

  return (
    <div
      className="markdown-content"
      dangerouslySetInnerHTML={{ __html: htmlContent }}
    />
  );
}
