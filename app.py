import streamlit as st
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import HumanMessage, AIMessage

import importlib
from src.agent.tools import construir_herramientas
try:
    from src.agent.agent_core import crear_agente_maestro, extraer_texto_respuesta
except ImportError:
    import src.agent.agent_core as agent_core_mod
    importlib.reload(agent_core_mod)
    from src.agent.agent_core import crear_agente_maestro, extraer_texto_respuesta

dir = [
    "data/documents",
    "data/spreadsheets"
]

st.set_page_config(page_title="Agente - Mercado", layout="centered")
st.title("Asistente Virtual - Mercado")
st.markdown("Consulta información sobre precios, productos y servicios.")

@st.cache_resource
def iniciar_sistema():
    load_dotenv()
    if "GEMINI_API_KEY" not in os.environ and "GEMINI_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]

    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.2)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    herramientas = construir_herramientas(llm, embeddings)
    agente = crear_agente_maestro(llm, herramientas)
    return agente

agente_ejecutor = iniciar_sistema()

st.markdown(
    """
    <style>
        [data-testid="stSidebarUserContent"] {
            display: flex;
            flex-direction: column;
            justify-content: center;
            height: 100%;
        }
    </style>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    st.markdown("### Mercado Agent")
    st.caption("Asistente Virtual de Inteligencia Artificial")
    
    archivos_cargados = []
    for directorio in dir:
        if os.path.exists(directorio):
            for archivo in os.scandir(directorio):
                if archivo.is_file() and archivo.name.endswith((".pdf", ".xls", ".xlsx")):
                    archivos_cargados.append(archivo.name)

    items_html = "".join([
        f"<li>{nombre}</li>"
        for nombre in archivos_cargados
    ])

    st.markdown(
        f"""
        <div>
            <h4 style="font-size: 0.95rem; margin-top: 15px; margin-bottom: 8px;">Archivos cargados:</h4>
            <ul style="padding-left: 20px; margin: 0; font-size: 0.85rem; line-height: 1.5;">
                {items_html if items_html else "<li style='color:#888;'>No se encontraron archivos.</li>"}
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

if "mensajes_chat" not in st.session_state:
    st.session_state.mensajes_chat = []

for mensaje in st.session_state.mensajes_chat:
    rol = "user" if isinstance(mensaje, HumanMessage) else "assistant"
    with st.chat_message(rol):
        st.markdown(mensaje.content)

pregunta_usuario = st.chat_input("Escribe tu pregunta aquí...")

if pregunta_usuario:
    with st.chat_message("user"):
        st.markdown(pregunta_usuario)
    
    st.session_state.mensajes_chat.append(HumanMessage(content=pregunta_usuario))
    
    with st.chat_message("assistant"):
        with st.spinner("Buscando en la base de conocimiento..."):
            try:
                respuesta_agente = agente_ejecutor.invoke({"input": pregunta_usuario})
                texto_respuesta = extraer_texto_respuesta(respuesta_agente["output"])
                
                st.markdown(texto_respuesta)
                
                st.session_state.mensajes_chat.append(AIMessage(content=texto_respuesta))
                
            except Exception as e:
                st.error(f"Ocurrió un error al procesar tu solicitud: {e}")