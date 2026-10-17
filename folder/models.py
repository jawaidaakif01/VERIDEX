from typing import List, Optional
from pydantic import BaseModel


class TestCase(BaseModel):
    case_id: str
    question: str
    expected_word: str = ""

class RunRecord(BaseModel):
    case_id: str
    version: str
    run_number: int
    passed: bool
    output: str
    error: Optional[str] = None
    seconds: float


class AgentResult(BaseModel):
    output: str
    tools_called: List[str] = []
    steps: int = 0