"""
=============================================================================
Projeto: 01 — Chatbot de Suporte Full-Stack (AfesuTech / DIZZIE)
Camada: Camada 3 — API REST & Comunicação Web
Arquivo: backend/main.py

Descrição:
Servidor web RESTful construído em FastAPI para expor o ChatbotEngine,
fornecendo endpoints de chat, base de conhecimento, métricas operacionais
e registro de feedbacks de clientes com suporte completo a CORS para o
frontend React / Vite.
=============================================================================
"""

import sys
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Garante a importação do ChatbotEngine estando no diretório backend ou na raiz
try:
    from chatbot_engine import ChatbotEngine
except ImportError:
    from backend.chatbot_engine import ChatbotEngine

# Suporte a caracteres UTF-8 no console Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Inicialização da Aplicação FastAPI
# ---------------------------------------------------------------------------
app = FastAPI(
    title="DIZZIE - Chatbot de Suporte Inteligente API",
    description="API REST para atendimento ao cliente automatizado com IA e RAG para o e-commerce de moda DIZZIE.",
    version="1.0.0"
)

# 1. Configuração de CORS liberando todas as origens para o frontend Vite/React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa o motor do chatbot
engine = ChatbotEngine()


# ---------------------------------------------------------------------------
# 2. Modelos Pydantic (Validação e Serialização)
# ---------------------------------------------------------------------------
class MessageRequest(BaseModel):
    """Modelo para envio de mensagem do usuário."""
    message: str = Field(..., min_length=1, description="Texto da mensagem enviada pelo usuário")
    session_id: Optional[str] = Field("default", description="Identificador da sessão para histórico multi-turn")


class FeedbackRequest(BaseModel):
    """Modelo para registro de avaliação do atendimento (Like/Dislike)."""
    message_id: str = Field(..., description="Identificador único da mensagem avaliada")
    is_positive: bool = Field(..., description="True para Like (positivo), False para Dislike (negativo)")


class ChatResponse(BaseModel):
    """Modelo de resposta formatada do Chatbot."""
    message_id: Optional[str] = Field(None, description="Identificador único gerado para a mensagem")
    reply: str = Field(..., description="Conteúdo da resposta gerada pela IA ou motor léxico")
    source: str = Field(..., description="Origem da resposta: 'llm', 'knowledge_base', 'greeting' ou 'fallback'")
    confidence: float = Field(..., description="Índice de confiança da resposta (entre 0.0 e 1.0)")
    timestamp: float = Field(..., description="Timestamp Unix do momento da resposta")
    suggested_actions: List[str] = Field(default_factory=list, description="Lista de ações ou perguntas sugeridas")


# ---------------------------------------------------------------------------
# 3. Endpoints da API REST
# ---------------------------------------------------------------------------
@app.get("/", summary="Status da API e Catálogo de Endpoints")
async def root():
    """
    Retorna o status operacional da API e a lista de endpoints disponíveis.
    """
    return {
        "status": "online",
        "service": "AfesuTech / DIZZIE Chatbot API",
        "version": "1.0.0",
        "empresa": engine.knowledge_base.get("empresa", "DIZZIE"),
        "endpoints": {
            "status": "GET /",
            "chat": "POST /api/chat",
            "knowledge_base": "GET /api/knowledge-base",
            "metrics": "GET /api/metrics",
            "feedback": "POST /api/feedback",
            "docs_swagger": "GET /docs",
            "docs_redoc": "GET /redoc"
        }
    }


@app.post("/api/chat", response_model=ChatResponse, summary="Processar Mensagem do Usuário")
async def chat_endpoint(payload: MessageRequest):
    """
    Recebe a mensagem do cliente, processa através do ChatbotEngine (LLM ou motor léxico)
    e retorna a resposta detalhada com confiança e ações sugeridas.
    """
    try:
        response_data = engine.process_message(
            user_message=payload.message,
            session_id=payload.session_id or "default"
        )
        return ChatResponse(**response_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao processar mensagem: {str(e)}"
        )


@app.get("/api/knowledge-base", summary="Consultar Base de Conhecimento")
async def knowledge_base_endpoint():
    """
    Retorna a base de conhecimento institucional atualmente carregada no motor RAG.
    """
    return engine.knowledge_base


@app.get("/api/metrics", summary="Consultar Métricas de Atendimento")
async def metrics_endpoint():
    """
    Retorna o total de atendimentos realizados, contagem por canal (LLM/Base/Fallback)
    e a taxa de satisfação calculada dos clientes.
    """
    return engine.get_metrics()


@app.post("/api/feedback", summary="Registrar Avaliação de Atendimento")
async def feedback_endpoint(payload: FeedbackRequest):
    """
    Registra a avaliação de Like (positivo) ou Dislike (negativo) para uma resposta.
    """
    try:
        result = engine.register_feedback(
            message_id=payload.message_id,
            is_positive=payload.is_positive
        )
        return {
            "success": True,
            "message": "Feedback registrado com sucesso!",
            **result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao registrar feedback: {str(e)}"
        )


# ---------------------------------------------------------------------------
# 4. Bloco de Execução Principal (Uvicorn)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Iniciando servidor DIZZIE Chatbot API na porta 8000...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
