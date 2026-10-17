from pydantic import BaseModel, Field

class HoneytokenCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    kind: str = Field(default="API credential", max_length=60)
    environment: str = Field(default="Local demo", max_length=80)
    severity: str = Field(default="high", pattern="^(low|medium|high|critical)$")
