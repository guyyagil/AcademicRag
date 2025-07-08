import re
from typing import Tuple, List, Optional

def extract_citations(answer: str) -> List[str]:
    """
    Extract citations in the format [Document: filename, Section: ...] from the answer.
    """
    pattern = r"\[Document:.*?\]"
    return re.findall(pattern, answer)

def parse_llm_output(llm_output: str) -> dict:
    """
    Parse the LLM output to extract the answer and citations.
    """
    citations = extract_citations(llm_output)
    
    return {
        "answer": llm_output.strip(),
        "citations": citations
    }