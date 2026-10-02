"""
=============================================================================
Projeto: 01 — Chatbot de Suporte Full-Stack (AfesuTech / DIZZIE)
Camada: Camada 2 — Inteligência Artificial & PLN (AI Engine)
Arquivo: backend/chatbot_engine.py

Descrição:
Motor de Inteligência Artificial responsável por carregar a base de conhecimento,
calcular similaridade léxica, orquestrar a LLM (Groq API com Llama-3) com
ancoragem temporal, gerenciar histórico multi-turn, fornecer fallback robusto
e gerenciar métricas de atendimento.
=============================================================================
"""

import os
import sys
import json
import re
import time
import uuid
from datetime import datetime
from pathlib import Path
import urllib.request
import urllib.error

# Garante suporte a UTF-8 no terminal Windows para exibição de emojis e acentos
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


class ChatbotEngine:
    """
    Motor central de PLN e IA generativa do Chatbot de Suporte.
    Combina RAG com LLM (Groq / Llama-3) e motor léxico offline com fallback seguro.
    """

    # Lista abrangente de stopwords em português para filtragem léxica
    STOPWORDS = {
        "a", "ao", "aos", "aquela", "aquelas", "aquele", "aqueles", "aquilo", "as",
        "ate", "com", "como", "da", "das", "de", "dela", "delas", "dele", "deles",
        "depois", "do", "dos", "e", "ela", "elas", "ele", "eles", "em", "entre",
        "era", "eram", "eramos", "essa", "essas", "esse", "esses", "esta", "estao",
        "estas", "estava", "estavam", "este", "estes", "estou", "eu", "foi", "fomos",
        "foram", "ha", "isso", "isto", "ja", "lhe", "lhes", "mais", "mas", "me",
        "mesmo", "meu", "meus", "minha", "minhas", "muito", "na", "nas", "nao",
        "no", "nos", "nossa", "nossas", "nosso", "nossos", "num", "numa", "o",
        "os", "ou", "para", "pela", "pelas", "pelo", "pelos", "por", "qual",
        "quando", "que", "quem", "sao", "se", "seja", "sejam", "sem", "ser",
        "seu", "seus", "so", "sua", "suas", "tambem", "te", "tem", "temos",
        "tenho", "ter", "teu", "teus", "tinha", "tinham", "toda", "todas", "todo",
        "todos", "tu", "tua", "tuas", "um", "uma", "umas", "uns", "voce", "voces"
    }

    # Padrões comuns de saudações em português
    GREETINGS_PATTERN = re.compile(
        r"\b(ol[aá]|oi|oie|bom dia|boa tarde|boa noite|e a[ií]|eai|hello|hey|opa)\b",
        re.IGNORECASE
    )

    def __init__(self, kb_path: str = None):
        """
        Inicializa o motor carregando variáveis de ambiente,
        base de conhecimento, histórico de conversação e métricas.
        """
        # Carrega variáveis do arquivo .env (caso exista)
        self._load_env_file()

        # Configurações do Groq e LLM
        self.groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
        self.groq_api_url = "https://api.groq.com/openai/v1/chat/completions"

        # Histórico de conversação multi-turn por sessão (session_id -> list[dict])
        self.conversations = {}

        # Dicionário de métricas de atendimento
        self.metrics = {
            "total_messages": 0,
            "resolved_by_llm": 0,
            "resolved_by_knowledge_base": 0,
            "fallback_count": 0,
            "positive_feedbacks": 0,
            "negative_feedbacks": 0
        }

        # Armazenamento de avaliações por message_id
        self.feedbacks = {}

        # Limiar de similaridade para motor léxico (0.0 a 1.0)
        self.similarity_threshold = 0.20

        # Carregamento da base de conhecimento
        self.kb_path = Path(kb_path) if kb_path else Path(__file__).parent / "base_conhecimento.json"
        self.knowledge_base = self._load_knowledge_base()

    def _load_env_file(self):
        """
        Lê arquivos .env locais nativamente sem exigir dependências externas pesadas.
        Busca no diretório backend e na raiz do projeto.
        """
        candidate_paths = [
            Path(__file__).parent / ".env",
            Path(__file__).parent.parent / ".env",
            Path(__file__).parent.parent / "Prompts" / "API.txt"
        ]

        for path in candidate_paths:
            if path.is_file():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if not line or line.startswith("#"):
                                continue
                            if "=" in line:
                                key, value = line.split("=", 1)
                                os.environ.setdefault(key.strip(), value.strip().strip("\"'"))
                            elif line.startswith("gsk_"):
                                # Suporte a arquivo de API que contenha apenas a chave Groq
                                os.environ.setdefault("GROQ_API_KEY", line.strip())
                except Exception as e:
                    print(f"[Aviso] Falha ao ler {path}: {e}")

    def _load_knowledge_base(self) -> dict:
        """
        Carrega o arquivo JSON da base de conhecimento factual.
        """
        if not self.kb_path.is_file():
            print(f"[Aviso] Arquivo de base de conhecimento não encontrado em: {self.kb_path}")
            return {
                "empresa": "DIZZIE",
                "descricao": "Loja de moda contemporânea e atendimento inteligente com IA.",
                "topicos": [],
                "faq_rapido": []
            }

        try:
            with open(self.kb_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except Exception as e:
            print(f"[Erro] Falha ao decodificar {self.kb_path}: {e}")
            return {
                "empresa": "DIZZIE",
                "descricao": "Loja de moda contemporânea e atendimento inteligente com IA.",
                "topicos": [],
                "faq_rapido": []
            }

    def _get_current_datetime_str(self) -> str:
        """
        Retorna a data e o horário atual por extenso em português para ancoragem temporal.
        """
        dias_semana = [
            "Segunda-feira", "Terça-feira", "Quarta-feira",
            "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"
        ]
        meses = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]

        agora = datetime.now()
        dia_semana = dias_semana[agora.weekday()]
        mes_nome = meses[agora.month - 1]

        return f"{dia_semana}, {agora.day:02d} de {mes_nome} de {agora.year}, às {agora.strftime('%H:%M')}"

    def _build_system_prompt(self) -> str:
        """
        Constrói o prompt de sistema injetando:
        1. Contexto institucional da empresa (DIZZIE).
        2. Base de conhecimento RAG (tópicos, perguntas e respostas).
        3. Ancoragem temporal real (data e hora atual em português).
        """
        empresa = self.knowledge_base.get("empresa", "DIZZIE")
        descricao = self.knowledge_base.get("descricao", "")
        topicos = self.knowledge_base.get("topicos", [])
        data_atual_extenso = self._get_current_datetime_str()

        # Compila os tópicos em formato textual para injeção de contexto RAG
        topicos_rag = []
        for topico in topicos:
            topico_id = topico.get("id", "")
            perguntas = ", ".join(f'"{p}"' for p in topico.get("perguntas_chave", []))
            resposta = topico.get("resposta", "")
            topicos_rag.append(
                f"### Tópico: [{topico_id}]\n"
                f"- Perguntas frequentes associadas: {perguntas}\n"
                f"- Resposta oficial e diretrizes:\n{resposta}\n"
            )
        base_rag_texto = "\n".join(topicos_rag)

        prompt = f"""Você é a assistente virtual inteligente da loja {empresa}.
Sua missão é atender clientes de forma amigável, acolhedora, moderna e eficiente, ajudando-os a encontrar peças que combinem com sua personalidade e solucionando dúvidas sobre compras, pedidos, tamanhos, entregas e trocas.

---
### 🏢 CONTEXTO DA EMPRESA:
{descricao}

---
### ⏰ ANCORAGEM TEMPORAL REAL:
Hoje é {data_atual_extenso}. Use esta informação caso o cliente pergunte sobre datas, prazos de entrega ou horários de atendimento.

---
### 📚 BASE DE CONHECIMENTO INSTITUCIONAL (RAG):
{base_rag_texto}

---
### 🎯 DIRETRIZES DE RESPOSTA:
1. Responda em Português do Brasil com tom simpático, elegante, acolhedor e profissional.
2. Utilize formatação Markdown rica (negrito, tópicos e espaçamento) e emojis adequados ao universo de moda e compras.
3. Se a pergunta do cliente estiver coberta pela base de conhecimento, utilize com precisão os dados oficiais (prazos de troca, condições de frete grátis, formas de pagamento com PIX 5% off, etc.).
4. Caso o cliente peça sugestões de looks ou estilo, aja como uma consultora de estilo com IA atenciosa e proativa.
5. Se o cliente perguntar algo completamente fora do escopo da loja ou que não possa ser respondido, oriente-o gentilmente aos canais de atendimento humano (WhatsApp e suporte@dizzie.com.br).
6. Mantenha respostas concisas, sem enrolação e fáceis de ler no celular.
"""
        return prompt

    def _call_groq_llm(self, user_message: str, session_id: str = "default") -> str:
        """
        Executa a requisição HTTP para a API Groq utilizando urllib nativo,
        preservando o histórico multi-turn da conversa.
        """
        if not self.groq_api_key:
            raise ValueError("Chave de API do Groq (GROQ_API_KEY) não configurada.")

        # Inicializa o histórico da sessão caso não exista
        if session_id not in self.conversations:
            self.conversations[session_id] = []

        system_prompt = self._build_system_prompt()

        # Monta a lista completa de mensagens (system + histórico recente + nova mensagem)
        messages_payload = [{"role": "system", "content": system_prompt}]

        # Adiciona até os últimos 8 turnos de conversa para economizar contexto
        messages_payload.extend(self.conversations[session_id][-8:])
        messages_payload.append({"role": "user", "content": user_message})

        payload = {
            "model": self.groq_model,
            "messages": messages_payload,
            "temperature": 0.6,
            "max_tokens": 1024
        }

        json_data = json.dumps(payload).encode("utf-8")

        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json",
            "User-Agent": "DizzieChatbotEngine/1.0"
        }

        req = urllib.request.Request(
            self.groq_api_url,
            data=json_data,
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=18) as response:
                response_body = response.read().decode("utf-8")
                data = json.loads(response_body)
                reply = data["choices"][0]["message"]["content"].strip()

                # Atualiza o histórico da sessão
                self.conversations[session_id].append({"role": "user", "content": user_message})
                self.conversations[session_id].append({"role": "assistant", "content": reply})

                return reply

        except urllib.error.HTTPError as e:
            error_msg = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"HTTP {e.code}")
        except Exception as e:
            raise e

    def _preprocess_text(self, text: str) -> list:
        """
        Pré-processa o texto para análise léxica:
        1. Converte para minúsculas.
        2. Remove pontuações e caracteres especiais.
        3. Remove stopwords em português.
        Retorna uma lista de tokens significativos.
        """
        if not text:
            return []

        # Minúsculas
        text = text.lower()

        # Remove acentuações simples para melhorar matching informal
        mapa_acentos = {
            'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a',
            'é': 'e', 'ê': 'e',
            'í': 'i',
            'ó': 'o', 'ô': 'o', 'õ': 'o',
            'ú': 'u', 'ü': 'u',
            'ç': 'c'
        }
        for char_acento, char_limpo in mapa_acentos.items():
            text = text.replace(char_acento, char_limpo)

        # Remove qualquer caractere que não seja letra ou número
        tokens_brutos = re.findall(r"\b[a-z0-9]+\b", text)

        # Filtra stopwords
        tokens = [t for t in tokens_brutos if t not in self.STOPWORDS and len(t) > 1]
        return tokens

    def _calculate_similarity(self, query_tokens: list, target_phrase: str) -> float:
        """
        Calcula a similaridade léxica através da taxa de sobreposição (Jaccard Overlap)
        entre os tokens da pergunta do usuário e os tokens da frase-alvo da base.
        """
        if not query_tokens:
            return 0.0

        target_tokens = self._preprocess_text(target_phrase)
        if not target_tokens:
            return 0.0

        set_query = set(query_tokens)
        set_target = set(target_tokens)

        intersecao = set_query.intersection(set_target)
        uniao = set_query.union(set_target)

        if not uniao:
            return 0.0

        # Média ponderada entre interseção sobre a query e Jaccard clássico
        # Isso beneficia perguntas curtas onde o usuário digita apenas termos-chave
        coverage_query = len(intersecao) / len(set_query)
        jaccard = len(intersecao) / len(uniao)

        return (coverage_query * 0.7) + (jaccard * 0.3)

    def _find_best_topic_offline(self, user_message: str):
        """
        Busca pelo tópico com maior similaridade léxica na base de conhecimento.
        Retorna (topico_encontrado, maior_similaridade).
        """
        query_tokens = self._preprocess_text(user_message)
        if not query_tokens:
            return None, 0.0

        best_topic = None
        best_score = 0.0

        for topico in self.knowledge_base.get("topicos", []):
            for pergunta in topico.get("perguntas_chave", []):
                score = self._calculate_similarity(query_tokens, pergunta)
                if score > best_score:
                    best_score = score
                    best_topic = topico

        return best_topic, best_score

    def _is_greeting(self, text: str) -> bool:
        """
        Identifica se a mensagem do usuário consiste primordialmente em uma saudação.
        """
        cleaned = text.strip().lower()
        if len(cleaned) <= 30 and self.GREETINGS_PATTERN.search(cleaned):
            return True
        return False

    def _get_greeting_response(self) -> str:
        """
        Retorna uma saudação padrão acolhedora apresentando a DIZZIE e seus tópicos.
        """
        empresa = self.knowledge_base.get("empresa", "DIZZIE")
        return (
            f"Olá! Seja muito bem-vinda(o) à **{empresa}**! ✨👗\n\n"
            "Eu sou sua assistente virtual de moda e atendimento. Como posso te encantar hoje?\n\n"
            "Aqui estão algumas coisas em que posso ajudar:\n"
            "* 📏 **Guia de Tamanhos e Medidas**\n"
            "* 🔁 **Trocas e Devoluções** (primeira troca grátis!)\n"
            "* 💳 **Pagamentos e Prazos de Frete**\n"
            "* 🪄 **Consultoria de Looks com IA**\n"
            "* 📍 **Rastreamento de Pedidos**\n\n"
            "Você pode me fazer uma pergunta ou escolher uma das opções rápidas abaixo! 💖"
        )

    def _get_fallback_response(self) -> str:
        """
        Retorna uma resposta elegante de fallback caso a LLM esteja indisponível
        e o motor léxico não tenha encontrado correspondência adequada.
        """
        empresa = self.knowledge_base.get("empresa", "DIZZIE")
        return (
            f"Desculpe, ainda não sei tudo sobre isso ou não compreendi completamente sua dúvida. 🥺\n\n"
            f"Na **{empresa}**, posso te ajudar com:\n"
            f"1. 📏 **Tamanhos e Medidas:** como medir busto, cintura e quadril.\n"
            f"2. 🔁 **Trocas e Devoluções:** prazos e logística reversa sem custo.\n"
            f"3. 💳 **Pagamento e Frete:** PIX com 5% de desconto e cálculo de frete.\n"
            f"4. 🪄 **Dicas de Looks:** sugestões de combinações com IA.\n"
            f"5. 📍 **Rastreio:** status do envio do seu pedido.\n\n"
            f"Se preferir falar com nosso time humano, estamos disponíveis no WhatsApp ou pelo e-mail "
            f"`suporte@dizzie.com.br` de segunda a sexta, das 09h às 18h! 💬"
        )

    def process_message(self, user_message: str, session_id: str = "default") -> dict:
        """
        Método principal de orquestração do chatbot:
        1. Atualiza métricas gerais.
        2. Detecta saudações diretas.
        3. Tenta processar via LLM (Groq / Llama-3) com RAG.
        4. Caso a LLM falhe ou não haja chave, utiliza o motor léxico na base factual.
        5. Se a similaridade for baixa, aciona o fallback elegante.
        """
        self.metrics["total_messages"] += 1
        message_id = str(uuid.uuid4())
        timestamp = time.time()
        suggested_actions = self.knowledge_base.get("faq_rapido", [])

        # 1. Detecção de saudações
        if self._is_greeting(user_message):
            return {
                "message_id": message_id,
                "reply": self._get_greeting_response(),
                "source": "greeting",
                "confidence": 1.0,
                "timestamp": timestamp,
                "suggested_actions": suggested_actions
            }

        # 2. Tentativa com LLM Generativa (Groq / Llama-3)
        if self.groq_api_key:
            try:
                llm_reply = self._call_groq_llm(user_message, session_id=session_id)
                self.metrics["resolved_by_llm"] += 1
                return {
                    "message_id": message_id,
                    "reply": llm_reply,
                    "source": "llm",
                    "confidence": 0.95,
                    "timestamp": timestamp,
                    "suggested_actions": suggested_actions
                }
            except Exception as e:
                # Alterna automaticamente para o motor léxico offline caso haja indisponibilidade da API
                pass

        # 3. Motor Léxico Offline (Fallback Semântico/Léxico)
        best_topic, score = self._find_best_topic_offline(user_message)

        if best_topic and score >= self.similarity_threshold:
            self.metrics["resolved_by_knowledge_base"] += 1
            return {
                "message_id": message_id,
                "reply": best_topic["resposta"],
                "source": "knowledge_base",
                "confidence": round(float(score), 2),
                "timestamp": timestamp,
                "suggested_actions": suggested_actions
            }

        # 4. Fallback Geral
        self.metrics["fallback_count"] += 1
        return {
            "message_id": message_id,
            "reply": self._get_fallback_response(),
            "source": "fallback",
            "confidence": round(float(score), 2),
            "timestamp": timestamp,
            "suggested_actions": suggested_actions
        }

    def register_feedback(self, message_id: str, is_positive: bool) -> dict:
        """
        Registra o feedback do usuário (Like/Dislike) e atualiza as métricas de satisfação.
        """
        self.feedbacks[message_id] = is_positive
        if is_positive:
            self.metrics["positive_feedbacks"] += 1
        else:
            self.metrics["negative_feedbacks"] += 1

        total_feedbacks = self.metrics["positive_feedbacks"] + self.metrics["negative_feedbacks"]
        satisfaction_rate = (
            round((self.metrics["positive_feedbacks"] / total_feedbacks) * 100, 1)
            if total_feedbacks > 0 else 100.0
        )

        return {
            "message_id": message_id,
            "is_positive": is_positive,
            "total_feedbacks": total_feedbacks,
            "satisfaction_rate": satisfaction_rate
        }

    def get_metrics(self) -> dict:
        """
        Retorna o sumário de métricas acumuladas e a taxa de satisfação atual.
        """
        total_feedbacks = self.metrics["positive_feedbacks"] + self.metrics["negative_feedbacks"]
        satisfaction_rate = (
            round((self.metrics["positive_feedbacks"] / total_feedbacks) * 100, 1)
            if total_feedbacks > 0 else 100.0
        )

        return {
            **self.metrics,
            "total_feedbacks": total_feedbacks,
            "satisfaction_rate": satisfaction_rate
        }


if __name__ == "__main__":
    # Teste rápido manual de inicialização e funcionamento do motor
    print("=== Inicializando ChatbotEngine para Testes Rápidos ===")
    engine = ChatbotEngine()
    print(f"Base carregada: {engine.knowledge_base.get('empresa')} ({len(engine.knowledge_base.get('topicos', []))} tópicos)")
    print(f"Groq API Key detectada: {'Sim' if engine.groq_api_key else 'Não'}")

    res_saudacao = engine.process_message("Olá, boa tarde!")
    print(f"\n[Teste 1 - Saudação] Fonte: {res_saudacao['source']} | Confiança: {res_saudacao['confidence']}")

    res_lexico = engine.process_message("Vocês têm tabela de medidas?")
    print(f"\n[Teste 2 - Pergunta da Base] Fonte: {res_lexico['source']} | Confiança: {res_lexico['confidence']}")
    print(f"Resposta prévia:\n{res_lexico['reply'][:120]}...")

    print("\nMétricas:", engine.get_metrics())
