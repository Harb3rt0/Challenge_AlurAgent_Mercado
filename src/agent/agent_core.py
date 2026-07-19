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