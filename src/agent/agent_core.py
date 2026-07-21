from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent

def crear_agente_maestro(llm, herramientas):
    system_instruction = (
        "Eres un asistente conversacional avanzado de Inteligencia Artificial.\n"
        "Cuentas con herramientas específicas para buscar en documentos PDF y una hoja de cálculo.\n\n"
        "Tus reglas obligatorias de comportamiento son:\n"
        "1. Analiza con cuidado la solicitud del usuario y decide qué herramienta invocar.\n"
        "2. Si la respuesta requiere datos exactos de la tabla o de los PDFs, usa la herramienta antes de responder.\n"
        "3. REGLA ESTRICTA DE CONTROL: Si tras usar tus herramientas la información no se encuentra allí, "
        "o el usuario te pregunta algo fuera de tu alcance (como cultura general o internet), debes responder "
        "textualmente: 'Lo siento, de momento no cuento con esa información en mi base de conocimiento.'\n"
        "4. Responde siempre en español con un lenguaje natural, profesional y claro."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_instruction),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])

    agent = create_tool_calling_agent(llm, herramientas, prompt)
    
    return AgentExecutor(agent=agent, tools=herramientas, verbose=True)

def extraer_texto_respuesta(salida):
    if isinstance(salida, str):
        return salida
    if isinstance(salida, list):
        partes = []
        for item in salida:
            if isinstance(item, dict) and "text" in item:
                partes.append(item["text"])
            elif isinstance(item, str):
                partes.append(item)
            elif hasattr(item, "text"):
                partes.append(getattr(item, "text"))
        if partes:
            return "\n".join(partes)
    if isinstance(salida, dict) and "text" in salida:
        return salida["text"]
    return str(salida)

def formatear_mensaje_error(e: Exception) -> str:
    msg = str(e)
    
    if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "Quota exceeded" in msg:
        return "Se ha alcanzado el límite de cuota de la API de Gemini (Error 429). Por favor, espera unos momentos antes de realizar otra pregunta."
    
    if "API_KEY_INVALID" in msg or "API key not found" in msg or "UNAUTHENTICATED" in msg:
        return "Error de autenticación con la API de Gemini. Por favor, verifica que la clave GEMINI_API_KEY esté configurada correctamente."
        
    if "ConnectionError" in msg or "TIMEOUT" in msg or "Unavailable" in msg:
        return "No se pudo establecer conexión con el servicio de Inteligencia Artificial. Por favor, verifica tu conexión a internet e intenta de nuevo."

    lineas = msg.splitlines()
    if lineas:
        primera_linea = lineas[0].strip()
        if "{" in primera_linea:
            primera_linea = primera_linea.split("{")[0].strip()
        if primera_linea:
            return f"Ocurrió un error al procesar tu solicitud: {primera_linea}"

    return "Ocurrió un error inesperado al procesar tu solicitud. Por favor, intenta nuevamente."

