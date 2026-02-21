import os
import sys

# Garante que o Python encontre a pasta src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

try:
    from src.core.graph import app
    print("LOG: Grafo carregado com sucesso.")
except ImportError as e:
    print(f"ERRO DE IMPORTAÇÃO: {e}")
    sys.exit(1)

def run_analysis(ticker: str):
    print(f"LOG: Iniciando análise para {ticker}...")
    
    config = {"configurable": {"thread_id": "teste_01"}}
    initial_state = {
        "target_ticker": ticker,
        "messages": []
    }
    
    try:
        # Loop de execução do Grafo
        for event in app.stream(initial_state, config):
            for node, data in event.items():
                print(f"\n--- Nó: {node.upper()} ---")
                if "messages" in data and data["messages"]:
                    print(f"Resposta: {data['messages'][-1]['content']}")
    except Exception as e:
        print(f"ERRO DURANTE A EXECUÇÃO: {e}")

if __name__ == "__main__":
    print("LOG: Script main.py iniciado.")
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERRO CRÍTICO: Variável GOOGLE_API_KEY não encontrada no ambiente!")
        print("DICA: Execute 'export GOOGLE_API_KEY=sua_chave' antes de rodar.")
    else:
        run_analysis("PETR4")