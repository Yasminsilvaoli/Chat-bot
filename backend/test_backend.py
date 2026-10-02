"""
=============================================================================
Projeto: 01 — Chatbot de Suporte Full-Stack (AfesuTech / DIZZIE)
Camada: Camada 2/3 — Validação & Qualidade de Software
Arquivo: backend/test_backend.py

Descrição:
Script automatizado de testes de terminal para validar o funcionamento
do ChatbotEngine em cenários de saudações, consultas à base de conhecimento
e perguntas técnicas de integração.
=============================================================================
"""

import sys
import os

# Suporte a caracteres UTF-8 no console Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Adiciona o diretório atual ao sys.path para garantir importação correta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chatbot_engine import ChatbotEngine


def run_tests():
    print("\n" + "=" * 65)
    print("🤖  INICIANDO BATERIA DE TESTES AUTOMATIZADOS - CHATBOT ENGINE")
    print("=" * 65)

    # 1. Inicializa o motor do chatbot
    engine = ChatbotEngine()

    # Informações institucionais e status da LLM
    empresa = engine.knowledge_base.get("empresa", "DIZZIE")
    total_topicos = len(engine.knowledge_base.get("topicos", []))
    tem_chave_llm = bool(engine.groq_api_key)

    print(f"🏢 Empresa Base: {empresa}")
    print(f"📚 Base de Conhecimento: {total_topicos} tópicos carregados")
    print(f"🧠 Status da LLM (Groq / Llama-3):", end=" ")
    if tem_chave_llm:
        print(f"Configurada (Modelo: {engine.groq_model})")
    else:
        print("Modo Offline (Motor Léxico Ativo)")
    print("-" * 65)

    # Lista de cenários de teste exigidos
    test_cases = [
        {
            "id": 1,
            "title": "Saudação do Usuário",
            "prompt": "Olá, tudo bem?",
            "expected_source": ["greeting", "llm"],
            "min_confidence": 0.5
        },
        {
            "id": 2,
            "title": "Pergunta Existente na Base (Planos e Preços)",
            "prompt": "Quais são os planos e preços?",
            "expected_source": ["knowledge_base", "llm"],
            "min_confidence": 0.2
        },
        {
            "id": 3,
            "title": "Pergunta sobre Integração (React e Python)",
            "prompt": "Como faço a integração com React e Python?",
            "expected_source": ["knowledge_base", "llm"],
            "min_confidence": 0.2
        }
    ]

    all_passed = True

    for test in test_cases:
        print(f"\n[TESTE {test['id']}] {test['title']}")
        print(f"❓ Pergunta: \"{test['prompt']}\"")

        # Processa mensagem no engine
        result = engine.process_message(test["prompt"], session_id=f"test_session_{test['id']}")

        reply = result.get("reply", "").strip()
        source = result.get("source", "desconhecido")
        confidence = result.get("confidence", 0.0)

        # Exibe resposta e métricas do teste
        print(f"🏷️  Fonte da Resposta: {source}")
        print(f"📊 Confiança: {confidence:.2f} ({confidence * 100:.0f}%)")
        print("💬 Resposta Obtida:")
        # Indenta a resposta para leitura limpa no terminal
        preview_lines = reply.split("\n")
        for line in preview_lines[:6]:
            print(f"    {line}")
        if len(preview_lines) > 6:
            print(f"    ... ({len(preview_lines) - 6} linhas adicionais)")

        # Validação do teste
        is_valid_reply = len(reply) > 10
        is_valid_conf = confidence >= test["min_confidence"]

        if is_valid_reply and is_valid_conf:
            print(f"Status: [OK] Teste {test['id']} passou com sucesso!")
        else:
            print(f"Status: [FALHA] Teste {test['id']} não atingiu os critérios esperados.")
            all_passed = False

        print("-" * 65)

    # Exibição de métricas finais
    metrics = engine.get_metrics()
    print("\n📈 RESUMO DAS MÉTRICAS ACUMULADAS:")
    print(f"   • Total de Mensagens Processadas: {metrics['total_messages']}")
    print(f"   • Resolvidas por LLM: {metrics['resolved_by_llm']}")
    print(f"   • Resolvidas por Base/Léxico: {metrics['resolved_by_knowledge_base']}")
    print(f"   • Fallbacks Ativados: {metrics['fallback_count']}")

    print("\n" + "=" * 65)
    if all_passed:
        print("🎉 [OK] TODOS OS TESTES PASSARAM COM SUCESSO! SISTEMA 100% OPERACIONAL.")
    else:
        print("⚠️ [AVISO] ALGUNS TESTES APRESENTARAM INCONSISTÊNCIAS.")
    print("=" * 65 + "\n")

    return all_passed


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
