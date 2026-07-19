import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from src.agent.tools import construir_herramientas
from src.agent.agent_core import crear_agente_maestro

# load_dotenv()

# GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# if not GEMINI_API_KEY:
#     raise ValueError("No se definió la clave API de Gemini")

load_dotenv()

def ejecutar_sistema():
    print("[Sistema] Inicializando modelos de Gemini...")
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.2)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    print("[Sistema] Cargando herramientas y archivos locales...")
    herramientas = construir_herramientas(llm, embeddings)

    print("[Sistema] Configurando cerebro del agente...")
    agente_final = crear_agente_maestro(llm, herramientas)
    
    print("\n=== AGENTE INTEGRADO Y LISTO ===")
    
    while True:
        pregunta = input("\n[Usuario] (escribe 'salir' para terminar): ")
        if pregunta.lower() == 'salir':
            break
        
        print("[Agente pensando...]")
        respuesta = agente_final.invoke({"input": pregunta})
        print(f"\n[Agente]: {respuesta['output']}")

if __name__ == "__main__":
    ejecutar_sistema()