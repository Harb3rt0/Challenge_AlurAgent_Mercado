import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
import importlib
from src.agent.tools import construir_herramientas
try:
    from src.agent.agent_core import crear_agente_maestro, extraer_texto_respuesta, formatear_mensaje_error
except ImportError:
    import src.agent.agent_core as agent_core_mod
    importlib.reload(agent_core_mod)
    from src.agent.agent_core import crear_agente_maestro, extraer_texto_respuesta, formatear_mensaje_error

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
        try:
            respuesta = agente_final.invoke({"input": pregunta})
            texto_limpio = extraer_texto_respuesta(respuesta["output"])
            print(f"\n[Agente]: {texto_limpio}")
        except Exception as e:
            print(f"\n[Error]: {formatear_mensaje_error(e)}")

if __name__ == "__main__":
    ejecutar_sistema()