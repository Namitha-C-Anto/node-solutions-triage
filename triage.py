import os
from pydantic import BaseModel, Field
from typing import Literal
from prompts import prompt
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv(override=True)

class TriageResult(BaseModel):
    """Structured triage result for an incoming client request."""
 
    summary: str = Field(description="1-2 sentence summary of the request")
    category: Literal["Sales", "Support", "Billing", "Technical", "Other"]
    priority: Literal["Low", "Medium", "High", "Urgent"]
    priority_reason: str = Field(description="Brief reason for the priority level")
    routed_to: Literal["Sales Team", "Client Success", "Finance", "Engineering"]
    draft_response: str = Field(description="Professional first response a team member could review and send")

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0, api_key=os.getenv("GROQ_API_KEY"))
structured_llm = llm.with_structured_output(TriageResult)
 
chain = prompt | structured_llm
 
def triage_request(request_text: str) -> TriageResult:
    return chain.invoke({"request": request_text})
 
# if __name__ == "__main__":
#     result = triage_request("We accidentally uploaded a spreadsheet containing customer contact information to the wrong workspace. We need immediate help removing access.")
#     print(result)