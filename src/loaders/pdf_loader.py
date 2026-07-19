import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

import time
from langchain_core.embeddings import Embeddings

class RetryEmbeddings(Embeddings):
    def __init__(self, wrapped_embeddings: Embeddings):
        self.wrapped_embeddings = wrapped_embeddings

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        results = []
        for text in texts:
            retries = 8
            delay = 10
            while retries > 0:
                try:
                    emb = self.wrapped_embeddings.embed_documents([text])[0]
                    results.append(emb)
                    break
                except Exception as e:
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        print(f"[RetryEmbeddings] Límite de cuota alcanzado (429) al procesar documento. Esperando {delay} segundos antes de reintentar...")
                        time.sleep(delay)
                        retries -= 1
                        delay = min(delay * 2, 60)
                    else:
                        raise e
            else:
                raise RuntimeError("Excedido el número máximo de reintentos para la generación de embeddings debido a límites de cuota (429).")
        return results

    def embed_query(self, text: str) -> list[float]:
        retries = 8
        delay = 10
        while retries > 0:
            try:
                return self.wrapped_embeddings.embed_query(text)
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    print(f"[RetryEmbeddings] Límite de cuota alcanzado (429) al procesar consulta. Esperando {delay} segundos antes de reintentar...")
                    time.sleep(delay)
                    retries -= 1
                    delay = min(delay * 2, 60)
                else:
                    raise e
        raise RuntimeError("Excedido el número máximo de reintentos para la generación de embeddings de consulta debido a límites de cuota (429).")

def inicializar_base_vectorial(embeddings_model):
    persist_dir = "database"
    embeddings_model_retry = RetryEmbeddings(embeddings_model)
    
    # Si la base de datos ya existe y no está vacía, la cargamos directamente
    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        print(f"[Cargador] Cargando base vectorial existente desde '{persist_dir}'...")
        vector_store = Chroma(persist_directory=persist_dir, embedding_function=embeddings_model_retry)
        return vector_store.as_retriever(search_kwargs={"k": 3})

    print(f"[Cargador] No se encontró una base vectorial. Inicializando nueva base...")
    pdf_path = "data/documents/"
    documentos_totales = []
    
    if not os.path.exists(pdf_path) or not os.listdir(pdf_path):
        raise FileNotFoundError(f"La carpeta {pdf_path} está vacía o no existe")

    for archivo in os.listdir(pdf_path):
        if archivo.endswith(".pdf"):
            ruta_completa = os.path.join(pdf_path, archivo)
            print(f"[Cargador] Procesando: {archivo}...")
            loader = PyPDFLoader(ruta_completa)
            documentos_totales.extend(loader.load())
            
    print(f"[Cargador] Total de páginas cargadas: {len(documentos_totales)}")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    fragmentos = text_splitter.split_documents(documentos_totales)

    print(f"[Cargador] Generando embeddings para {len(fragmentos)} fragmentos...")
    # Inicializamos Chroma vacío en el persist_directory
    vector_store = Chroma(persist_directory=persist_dir, embedding_function=embeddings_model_retry)
    
    # Agregamos los documentos en lotes con un retraso para no agotar la cuota de la API de Gemini (Free Tier)
    chunk_batch_size = 50
    for i in range(0, len(fragmentos), chunk_batch_size):
        lote = fragmentos[i:i + chunk_batch_size]
        print(f"[Cargador] Procesando lote {i//chunk_batch_size + 1}: fragmentos {i+1} a {min(i + chunk_batch_size, len(fragmentos))}...")
        vector_store.add_documents(lote)
        if i + chunk_batch_size < len(fragmentos):
            print("[Cargador] Esperando 10 segundos para no saturar la cuota de la API...")
            time.sleep(10)
    
    return vector_store.as_retriever(search_kwargs={"k": 3})