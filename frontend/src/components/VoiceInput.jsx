/**
 * =============================================================================
 * Projeto: 01 — Chatbot de Suporte Full-Stack (AfesuTech / DIZZIE)
 * Camada: Camada 4 — Multimodalidade, Acessibilidade & Mobile
 * Arquivo: frontend/src/components/VoiceInput.jsx
 * 
 * Componente de entrada por voz nativa (STT) utilizando a Web Speech API
 * com suporte completo a celulares Android, iPhones (iOS) e computadores.
 * =============================================================================
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Mic, MicOff } from 'lucide-react';

export default function VoiceInput({ onTranscript, disabled = false }) {
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  // Limpeza de qualquer sessão ativa ao desmontar o componente
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch {
          // Ignora erros ao fechar silenciosamente
        }
        recognitionRef.current = null;
      }
    };
  }, []);

  /**
   * Inicializa e dispara o reconhecimento de voz nativo do navegador
   */
  const startListening = useCallback(() => {
    // 1. Validação de Contexto Seguro (HTTPS / Localhost)
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    if (!window.isSecureContext && !isLocalhost) {
      alert('⚠️ O microfone no celular exige conexão segura (HTTPS). Acesse via túnel HTTPS!');
      return;
    }

    // 2. Validação de Suporte à Web Speech API
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Seu navegador não suporta reconhecimento de voz nativo. Recomendamos Google Chrome ou Safari.');
      return;
    }

    // Cancela qualquer instância anterior para garantir inicialização limpa (essencial no mobile)
    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
      } catch {}
      recognitionRef.current = null;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.lang = 'pt-BR';
      recognition.continuous = false; // Modo single-phrase para máxima estabilidade em celulares
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      // Evento: Início da escuta
      recognition.onstart = () => {
        setIsListening(true);
      };

      // Evento: Fala reconhecida com sucesso
      recognition.onresult = (event) => {
        const transcript = event.results?.[0]?.[0]?.transcript;
        if (transcript && typeof onTranscript === 'function') {
          onTranscript(transcript.trim());
        }
      };

      // Evento: Tratamento detalhado de erros
      recognition.onerror = (event) => {
        console.warn('[Reconhecimento de Voz] Erro detectado:', event.error);
        setIsListening(false);

        switch (event.error) {
          case 'not-allowed':
          case 'service-not-allowed':
            alert('Permissão de microfone negada. Toque no ícone de cadeado/configurações do navegador e marque "Permitir Microfone".');
            break;
          case 'no-speech':
            // Usuário não falou nada no intervalo estipulado
            break;
          case 'audio-capture':
            alert('Nenhum microfone encontrado em seu dispositivo.');
            break;
          case 'network':
            alert('Erro de conexão ao processar áudio pela Web Speech API.');
            break;
          default:
            break;
        }
      };

      // Evento: Término da captura de áudio
      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
      recognition.start();

    } catch (err) {
      console.error('[Reconhecimento de Voz] Falha ao iniciar:', err);
      setIsListening(false);
    }
  }, [onTranscript]);

  /**
   * Interrompe manualmente a escuta caso o usuário clique novamente
   */
  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {}
    }
    setIsListening(false);
  }, []);

  /**
   * Alterna entre iniciar ou pausar a gravação de voz
   */
  const handleToggleVoice = () => {
    if (disabled) return;
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  return (
    <div style={{ position: 'relative', display: 'inline-flex', alignItems: 'center' }}>
      <button
        type="button"
        onClick={handleToggleVoice}
        disabled={disabled}
        className={`mic-btn ${isListening ? 'recording' : ''}`}
        title={isListening ? 'Parar gravação de voz' : 'Falar por voz (Microfone)'}
        aria-label={isListening ? 'Parar gravação de voz' : 'Falar por voz'}
      >
        {isListening ? (
          <MicOff size={20} className="mic-icon animate-pulse" />
        ) : (
          <Mic size={20} className="mic-icon" />
        )}
      </button>

      {/* Indicador animado flutuante quando o microfone está ativo */}
      {isListening && (
        <div className="listening-tooltip">
          🎙️ Ouvindo no celular... Fale agora!
        </div>
      )}
    </div>
  );
}
