from langchain_core.tools import tool
from src.loaders.xls_loader import cargar_datos_xls
from src.loaders.pdf_loader import inicializar_base_vectorial

def construir_herramientas(llm, embeddings_model):
    df_real = cargar_datos_xls()

    @tool
    def consultar_xls(pregunta_usuario: str) -> str:
        """Consulta la hoja de cálculo de inventario del supermercado para responder preguntas sobre productos, stock y precios."""
        contexto_tabla = df_real.to_markdown(index=False)
        prompt_interno = (
            f"Analiza la siguiente tabla de datos:\n\n{contexto_tabla}\n\n"
            f"Responde con precisión matemática y basándote únicamente en la tabla a la consulta: {pregunta_usuario}\n"
            f"Si la información no está en la tabla, responde de forma concisa: 'Dato no disponible en la hoja de cálculo'."
        )
        respuesta = llm.invoke(prompt_interno)
        return respuesta.content
    
    retriever = inicializar_base_vectorial(embeddings_model)

    @tool
    def herramienta_pdf(consulta: str) -> str:
        """Busca en los manuales de proveedores, políticas de compras, políticas de atención al cliente y reglamentos del supermercado para responder a consultas normativas."""
        documentos_relevantes = retriever.invoke(consulta)
        
        texto_extraido = "\n\n".join([doc.page_content for doc in documentos_relevantes])
        return texto_extraido

    return [consultar_xls, herramienta_pdf]