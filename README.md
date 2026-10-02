# 👗 Alaency — Chatbot Full-Stack com IA e Voz

Chatbot inteligente para atendimento ao cliente da marca de moda feminina **Alaency**, combinando **Python (FastAPI)**, **Inteligência Artificial (Groq / Llama-3 / RAG)**, **Reconhecimento de Voz (Web Speech API)** e **React (Vite)**.

---

## 🚀 Arquitetura do Projeto

* **Backend (`/backend`)**:
  * API REST com **FastAPI** e **Uvicorn**
  * Motor de IA com **Llama-3** (Groq API) e **RAG** com a base de conhecimento institucional (`base_conhecimento.json`)
  * Motor léxico e semântico offline para fallback automático
  * Métricas em tempo real e avaliação Like / Dislike
* **Frontend (`/frontend`)**:
  * **React 19** com **Vite**
  * Design System moderno com **Dark Mode**, **Glassmorphism** e cores da marca (Rosa, Verde Esmeralda e Dourado)
  * Entrada por voz nativa (STT) compatível com Mobile (Android e iOS) e Desktop
  * Formatação rica em Markdown com a biblioteca `marked`
  * Exportação de histórico de atendimento em `.txt`

---

## 🛠️ Como Executar Localmente

### 1. Backend (Python)
```bash
# Entrar no backend
cd backend

# Criar arquivo de variáveis a partir do modelo
copy .env.example .env

# Instalar dependências
pip install -r requirements.txt

# Iniciar o servidor
python main.py
```
> O backend estará rodando em: `http://localhost:8000`

### 2. Frontend (React / Vite)
```bash
# Entrar no frontend
cd frontend

# Instalar dependências
npm install

# Iniciar o ambiente de desenvolvimento
npm run dev
```
> O frontend estará rodando em: `http://localhost:5173`

---

## 🌐 Deploy na Vercel (Frontend)

1. Faça o fork ou importe o repositório no seu painel da [Vercel](https://vercel.com).
2. Se a Vercel solicitar o diretório raiz (**Root Directory**), selecione `frontend` (ou deixe a raiz, pois o `vercel.json` já está pré-configurado).
3. Caso queira apontar para uma URL de backend em produção, adicione a variável de ambiente:
   * `VITE_API_URL`: URL do seu backend em produção (ex: `https://sua-api.onrender.com` ou `https://sua-api.railway.app`).
4. Clique em **Deploy**!

---

## 🔒 Segurança e Privacidade
* Os arquivos `.env` contendo chaves de API sensíveis são estritamente ignorados pelo `.gitignore` e **nunca** sobem para o repositório ou frontend.
