import streamlit as st
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import HumanMessage, AIMessage

from src.agent.tools import construir_herramientas
from src.agent.agent_core import crear_agente_maestro

st.set_page_config(page_title="Agente - Mercado", layout="centered")
st.title("Asistente Virtual - Mercado")
st.markdown("Consulta información sobre precios, productos y servicios.")

@st.cache_resource
def iniciar_sistema():
    load_dotenv()
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.2)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    herramientas = construir_herramientas(llm, embeddings)
    agente = crear_agente_maestro(llm, herramientas)
    return agente

agente_ejecutor = iniciar_sistema()

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
                texto_respuesta = respuesta_agente["output"]
                
                st.markdown(texto_respuesta)
                
                st.session_state.mensajes_chat.append(AIMessage(content=texto_respuesta))
                
            except Exception as e:
                st.error(f"Ocurrió un error al procesar tu solicitud: {e}")