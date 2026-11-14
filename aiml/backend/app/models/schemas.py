from pydantic import BaseModel, Field
from typing import List

class CodeAnalysisRequest(BaseModel):
    code: str = Field(..., description="The Python source code snippet to be analyzed.")

class VulnerabilityItem(BaseModel):
    line: int = Field(..., description="Line number where the issue was detected.")
    severity: str = Field(..., description="Severity level: HIGH, MEDIUM, or LOW.")
    rule_id: str = Field(..., description="Unique rule identifier.")
    message: str = Field(..., description="Detailed explanation of the security risk.")

class CodeAnalysisResponse(BaseModel):
    status: str = Field("success")
    total_issues: int = Field(...)
    issues: List[VulnerabilityItem] = Field(...)