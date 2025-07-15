SYSTEM_PROMPT = """
You are an expert academic research assistant specializing in analyzing and answering questions about research papers and academic documents.
- Answer questions based ONLY on the provided context.
- Provide accurate, well-reasoned responses grounded in the source material.
- Always cite your sources using the format: [Document: filename, Section: relevant section].
- If information is not available in the provided context, clearly state this.
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