import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

def test_connection():
    print("--- Alinhamento Aequitas-MAS 2026 ---")
    
    try:
        # Configuração oficial validada: gemini-flash-latest
        llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            temperature=0
        )

        prompt = "Confirme recepção via endpoint estável v1."
        print(f"Enviando para: {llm.model}")
        
        response = llm.invoke([HumanMessage(content=prompt)])
        
        print(f"\nRESPOSTA: {response.content}")
        print("SUCESSO: Nó qualitativo restaurado.")

    except Exception as e:
        print(f"\nERRO: {e}")
        print("\nTentando reconexão...")
        try:
            llm_alt = ChatGoogleGenerativeAI(model="gemini-flash-latest")
            print(f"Sucesso com 'gemini-flash-latest': {llm_alt.invoke('Oi').content}")
        except:
            print("Falha total nos aliases conhecidos.")

if __name__ == "__main__":
    test_connection()