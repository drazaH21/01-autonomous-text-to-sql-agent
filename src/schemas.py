from pydantic import BaseModel, Field
from typing import Optional, List

class SQLQueryResponse(BaseModel):
    sql_query: str = Field(description="The executable SQL query for DuckDB based on the user request.")
    reasoning: str = Field(description="Brief explanation of why this SQL query was written.")

class AgentExecutionResult(BaseModel):
    user_query: str
    generated_sql: Optional[str] = None
    execution_success: bool
    raw_results: Optional[List[dict]] = None
    error_message: Optional[str] = None
    executive_summary: Optional[str] = None
    tokens_used_estimate: int = 0
