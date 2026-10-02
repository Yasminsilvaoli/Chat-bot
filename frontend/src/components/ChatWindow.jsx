/**
 * =============================================================================
 * Projeto: 01 — Chatbot de Suporte Full-Stack (AfesuTech / DIZZIE)
 * Camada: Camada 4 — Interface & Experiência do Usuário (UX)
 * Arquivo: frontend/src/components/ChatWindow.jsx
 * 
 * Componente principal da janela do Chatbot:
 * - Histórico multi-turn com auto-scroll suave
 * - Conexão HTTP REST com backend FastAPI (/api/chat, /api/feedback, /api/metrics)
 * - Entrada por voz com VoiceInput
 * - Chips de perguntas rápidas
 * - Feedback Like / Dislike
 * - Barra de métricas e exportação de histórico em .txt
 * =============================================================================
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Send, 
  Bot, 
  User, 
  ThumbsUp, 
  ThumbsDown, 
  Download, 
  Sparkles, 
  BarChart3, 
  RotateCcw,
  Clock
} from 'lucide-react';
import FormattedMessage from './FormattedMessage';
import VoiceInput from './VoiceInput';

// URL base da API FastAPI com fallback para porta 8000
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Utilitários de ID e Timestamp no escopo do módulo
let idCounter = 0;
function createMessageId(prefix) {
  idCounter += 1;
  return `${prefix}_${Date.now()}_${idCounter}`;
}

function getCurrentTimestamp() {
  return Date.now();
}

export default function ChatWindow() {
  // Identificador de sessão único para manter histórico multi-turn no backend
  const [sessionId] = useState(() => 'sess_' + Math.random().toString(36).substring(2, 9));

  // Estado do histórico de mensagens inicializado via função pura
  const [messages, setMessages] = useState(() => [
    {
      id: 'welcome_1',
      sender: 'bot',
      text: 'Olá! Seja muito bem-vinda à **Alaency**! ✨👗\n\nEu sou sua consultora virtual de moda e atendimento inteligente. Como posso te encantar hoje?\n\nVocê pode me perguntar sobre nosso guia de tamanhos, coleções exclusivas, prazos de entrega ou selecionar um dos atalhos abaixo! 💖',
      timestamp: 1727888400000,
      source: 'greeting',
      confidence: 1.0,
      feedback: null // 'like' | 'dislike' | null
    }
  ]);

  // Input de texto e controle de carregamento
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Ações sugeridas (chips de perguntas rápidas da Alaency)
  const [suggestedActions, setSuggestedActions] = useState([
    'Como saber o meu tamanho ideal na Alaency?',
    'Como funciona a política de trocas e devoluções?',
    'Qual o prazo de entrega e como rastrear meu pedido?',
    'Vocês montam looks personalizados com Inteligência Artificial?'
  ]);

  // Métricas do atendimento
  const [metrics, setMetrics] = useState({
    total_messages: 1,
    satisfaction_rate: 100.0,
    current_mode: 'RAG Base de Conhecimento'
  });

  // Referências para auto-scroll e foco
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  /**
   * Auto-scroll suave sempre que uma nova mensagem for inserida
   */
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, scrollToBottom]);

  /**
   * Carrega métricas consolidadas da API de forma assíncrona
   */
  useEffect(() => {
    let isMounted = true;

    async function loadInitialMetrics() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/metrics`);
        if (response.ok && isMounted) {
          const data = await response.json();
          setMetrics(prev => ({
            ...prev,
            total_messages: data.total_messages || prev.total_messages,
            satisfaction_rate: data.satisfaction_rate ?? prev.satisfaction_rate,
            current_mode: (data.resolved_by_llm > 0) ? 'LLM Ativa (Groq / Llama-3)' : 'RAG Base de Conhecimento'
          }));
        }
      } catch {
        // Falha silenciosa em caso de API temporariamente offline
      }
    }

    loadInitialMetrics();

    return () => {
      isMounted = false;
    };
  }, []);

  /**
   * Envia a mensagem do usuário para o backend
   */
  const handleSendMessage = async (textToSend) => {
    const messageText = (typeof textToSend === 'string' ? textToSend : inputValue).trim();
    if (!messageText || isLoading) return;

    // Cria a mensagem do usuário no histórico local
    const userMessage = {
      id: createMessageId('usr'),
      sender: 'user',
      text: messageText,
      timestamp: getCurrentTimestamp()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: messageText,
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`Erro na API (${response.status})`);
      }

      const data = await response.json();

      // Determina o modo operacional com base na fonte da resposta
      const modeLabel = data.source === 'llm' 
        ? 'LLM Ativa (Groq / Llama-3)' 
        : 'RAG Base de Conhecimento';

      // Cria a mensagem de resposta da IA
      const botMessage = {
        id: data.message_id || createMessageId('bot'),
        sender: 'bot',
        text: data.reply,
        timestamp: data.timestamp ? data.timestamp * 1000 : getCurrentTimestamp(),
        source: data.source,
        confidence: data.confidence,
        feedback: null
      };

      setMessages(prev => [...prev, botMessage]);

      // Atualiza perguntas sugeridas caso a API forneça novas
      if (Array.isArray(data.suggested_actions) && data.suggested_actions.length > 0) {
        setSuggestedActions(data.suggested_actions);
      }

      // Atualiza métricas
      setMetrics(prev => ({
        ...prev,
        total_messages: prev.total_messages + 2,
        current_mode: modeLabel
      }));

    } catch (error) {
      console.error('[ChatWindow] Falha ao enviar mensagem:', error);

      // Resposta amigável de erro de conexão
      const errorMessage = {
        id: createMessageId('err'),
        sender: 'bot',
        text: '⚠️ **Aviso de Conexão:** Não foi possível contactar o servidor no momento. Verifique se o backend FastAPI está em execução na porta 8000 e tente novamente em instantes!',
        timestamp: getCurrentTimestamp(),
        source: 'error',
        confidence: 0.0,
        feedback: null
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  /**
   * Trata o envio ao pressionar Enter no teclado
   */
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  /**
   * Recebe a transcrição de voz do VoiceInput e envia diretamente
   */
  const handleVoiceTranscript = (transcript) => {
    if (transcript) {
      setInputValue(transcript);
      handleSendMessage(transcript);
    }
  };

  /**
   * Registra a avaliação de Like / Dislike na API
   */
  const handleFeedback = async (messageId, isPositive) => {
    // Atualiza estado local imediatamente para feedback visual instantâneo
    setMessages(prev => prev.map(msg => {
      if (msg.id === messageId) {
        return {
          ...msg,
          feedback: isPositive ? 'like' : 'dislike'
        };
      }
      return msg;
    }));

    try {
      const response = await fetch(`${API_BASE_URL}/api/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message_id: messageId,
          is_positive: isPositive
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (typeof data.satisfaction_rate === 'number') {
          setMetrics(prev => ({
            ...prev,
            satisfaction_rate: data.satisfaction_rate
          }));
        }
      }
    } catch (err) {
      console.warn('[ChatWindow] Falha ao registrar feedback na API:', err);
    }
  };

  /**
   * Exporta todo o histórico de mensagens em arquivo de texto (.txt)
   */
  const handleExportHistory = () => {
    const header = [
      '==============================================================',
      '       HISTÓRICO DE ATENDIMENTO - ALAENCY MODA FEMININA & IA',
      `       Data de Exportação: ${new Date().toLocaleString('pt-BR')}`,
      `       Sessão: ${sessionId}`,
      '==============================================================\n\n'
    ].join('\n');

    const body = messages.map(msg => {
      const hora = new Date(msg.timestamp).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
      const autor = msg.sender === 'user' ? 'CLIENTE' : 'CONSULTORA ALAENCY';
      const cleanText = msg.text.replace(/[*_#`]/g, '');
      return `[${hora}] ${autor}:\n${cleanText}\n`;
    }).join('\n--------------------------------------------------------------\n\n');

    const fullContent = header + body;
    const blob = new Blob([fullContent], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `atendimento_alaency_${getCurrentTimestamp()}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  /**
   * Reinicia a conversa
   */
  const handleResetChat = () => {
    if (window.confirm('Deseja iniciar um novo atendimento? O histórico atual será limpo.')) {
      setMessages([
        {
          id: createMessageId('welcome'),
          sender: 'bot',
          text: 'Atendimento reiniciado! Como posso te ajudar agora? 👗✨',
          timestamp: getCurrentTimestamp(),
          source: 'greeting',
          confidence: 1.0,
          feedback: null
        }
      ]);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-card">

        {/* 1. Barra Superior de Métricas */}
        <div className="metrics-bar">
          <div className="metrics-group">
            <span className="metric-pill" title="Total de mensagens trocadas na sessão">
              <BarChart3 size={15} style={{ color: 'var(--accent-secondary)' }} />
              <span>Mensagens: <strong>{metrics.total_messages}</strong></span>
            </span>

            <span className="metric-pill" title="Taxa calculada de satisfação dos clientes">
              <Sparkles size={15} style={{ color: 'var(--status-online)' }} />
              <span>Satisfação: <strong>{metrics.satisfaction_rate}%</strong></span>
            </span>

            <span className="metric-pill" title="Modo operacional atual da IA">
              <Clock size={15} style={{ color: 'var(--accent-primary)' }} />
              <span>Modo: <strong>{metrics.current_mode}</strong></span>
            </span>
          </div>

          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <button 
              type="button" 
              onClick={handleResetChat} 
              className="export-btn"
              title="Reiniciar conversa"
            >
              <RotateCcw size={14} />
              <span>Limpar</span>
            </button>

            <button 
              type="button" 
              onClick={handleExportHistory} 
              className="export-btn"
              title="Baixar histórico completo em .txt"
            >
              <Download size={14} />
              <span>Exportar</span>
            </button>
          </div>
        </div>

        {/* 2. Área de Mensagens (Viewport com scroll suave) */}
        <div className="messages-viewport">
          {messages.map((msg) => {
            const isUser = msg.sender === 'user';
            const formattedTime = new Date(msg.timestamp).toLocaleTimeString('pt-BR', {
              hour: '2-digit',
              minute: '2-digit'
            });

            return (
              <div key={msg.id} className={`message-row ${isUser ? 'user' : 'bot'}`}>
                <div className={`avatar ${isUser ? 'user' : 'bot'}`}>
                  {isUser ? <User size={18} /> : <Bot size={18} />}
                </div>

                <div className="message-bubble">
                  {isUser ? (
                    <p style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</p>
                  ) : (
                    <FormattedMessage content={msg.text} />
                  )}

                  {/* Metadados e ações da mensagem */}
                  <div className="message-meta">
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                      <span>{formattedTime}</span>
                      {!isUser && msg.source && (
                        <span className="source-tag">{msg.source}</span>
                      )}
                    </span>

                    {/* Botões de Like / Dislike apenas nas respostas da IA */}
                    {!isUser && msg.source !== 'error' && (
                      <div className="feedback-actions">
                        <button
                          type="button"
                          onClick={() => handleFeedback(msg.id, true)}
                          className={`feedback-btn ${msg.feedback === 'like' ? 'active like' : ''}`}
                          title="Resposta útil (Gostei)"
                          aria-label="Avaliar como positivo"
                        >
                          <ThumbsUp size={14} />
                        </button>
                        <button
                          type="button"
                          onClick={() => handleFeedback(msg.id, false)}
                          className={`feedback-btn ${msg.feedback === 'dislike' ? 'active dislike' : ''}`}
                          title="Não ajudou (Não gostei)"
                          aria-label="Avaliar como negativo"
                        >
                          <ThumbsDown size={14} />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}

          {/* Indicador visual "IA digitando..." */}
          {isLoading && (
            <div className="message-row bot">
              <div className="avatar bot">
                <Bot size={18} />
              </div>
              <div className="typing-indicator">
                <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginRight: '6px' }}>
                  Alaency está digitando
                </span>
                <span className="typing-dot" />
                <span className="typing-dot" />
                <span className="typing-dot" />
              </div>
            </div>
          )}

          {/* Âncora invisível para o auto-scroll */}
          <div ref={messagesEndRef} />
        </div>

        {/* 3. Chips de Perguntas Rápidas (Suggested Actions) */}
        {suggestedActions && suggestedActions.length > 0 && (
          <div className="chips-container">
            <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)', whiteSpace: 'nowrap' }}>
              💡 Sugestões:
            </span>
            {suggestedActions.map((action, idx) => (
              <button
                key={idx}
                type="button"
                className="chip-btn"
                onClick={() => handleSendMessage(action)}
                disabled={isLoading}
              >
                {action}
              </button>
            ))}
          </div>
        )}

        {/* 4. Barra Inferior de Entrada (Input, Voz e Envio) */}
        <div className="chat-input-area">
          <div className="input-wrapper">
            <input
              ref={inputRef}
              type="text"
              className="chat-input"
              placeholder="Digite sua dúvida ou fale pelo microfone..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
            />
          </div>

          {/* Componente de Reconhecimento de Voz */}
          <VoiceInput
            onTranscript={handleVoiceTranscript}
            disabled={isLoading}
          />

          {/* Botão de Enviar */}
          <button
            type="button"
            className="send-btn"
            onClick={() => handleSendMessage()}
            disabled={isLoading || !inputValue.trim()}
            title="Enviar mensagem"
            aria-label="Enviar mensagem"
          >
            <Send size={18} />
          </button>
        </div>

      </div>
    </div>
  );
}
