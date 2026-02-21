import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

def test_connection():
    print("--- Alinhamento Aequitas-MAS 2026 ---")
    
    try:
        # A recomendação atual é usar o modelo estável ou o sucessor direto
        # Tente 'gemini-1.5-flash' ou o novo 'gemini-2.0-flash' se sua chave permitir
        llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest", # <--- Use este alias, ele é o mais estável para v1
            temperature=0
        )

        prompt = "Confirme recepção via endpoint estável v1."
        print(f"Enviando para: {llm.model}")
        
        response = llm.invoke([HumanMessage(content=prompt)])
        
        print(f"\nRESPOSTA: {response.content}")
        print("SUCESSO: Nó qualitativo restaurado.")

    except Exception as e:
        print(f"\nERRO: {e}")
        print("\nTentando com nomenclatura de 2026...")
        try:
            # Algumas chaves agora exigem o alias simplificado
            llm_alt = ChatGoogleGenerativeAI(model="gemini-flash-latest")
            print(f"Sucesso com 'gemini-flash-latest': {llm_alt.invoke('Oi').content}")
        except:
            print("Falha total nos aliases conhecidos.")

if __name__ == "__main__":
    test_connection()