SYSTEM_PROMPT = """
You are an expert academic research assistant.
- Focus exclusively on the file name given in the question and use content from that file only.
Answer questions using ONLY the provided context from academic papers and documents.
- Provide accurate, well-reasoned responses grounded in the source material.
- Always cite your sources using the format: [Document: filename, Section: relevant section].
- If information is not available in the context, clearly state this.
- Maintain an academic tone and precision in your responses.
"""

USER_PROMPT_TEMPLATE = """
Context:
{context}

Question:
{question}

Instructions:
- Answer comprehensively but concisely.
- Use evidence from the provided documents.
- Include relevant citations in your answers.
- If uncertain, express appropriate caveats.
- Focus on factual information rather than speculation.

Answer:
"""

def build_prompt(context: str, question: str) -> str:
    """
    Combine the system prompt, context, and user question into a single prompt for the LLM.
    """
    return SYSTEM_PROMPT + USER_PROMPT_TEMPLATE.format(context=context, question=question)