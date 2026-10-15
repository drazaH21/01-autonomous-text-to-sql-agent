import os
import json
from dotenv import load_dotenv
from groq import Groq
from src.database import init_sample_db, get_table_schema
from src.tools import execute_sql_safely
from src.schemas import AgentExecutionResult

load_dotenv()

class TextToSQLAgent:
    def __init__(self, model_name: str = "openai/gpt-oss-20b"):
        init_sample_db()
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model_name = model_name
        self.schema_str = get_table_schema()

    def run(self, user_query: str) -> AgentExecutionResult:
        total_tokens_est = 0
        max_retries = 3
        current_try = 0
        sql_query = None
        execution_output = None

        system_prompt = (
            "You are an expert Text-to-SQL Data Analyst agent. "
            "Your job is to convert natural language questions into valid DuckDB SQL queries. "
            "You must output ONLY valid JSON with keys: 'sql_query' and 'reasoning'. "
            "Do not include markdown backticks or extra text outside the JSON."
        )

        while current_try < max_retries:
            current_try += 1
            
            if current_try == 1:
                user_prompt = (
                    f"Database Schema:\n{self.schema_str}\n\n"
                    f"User Question: {user_query}\n\n"
                    "Return a JSON object with 'sql_query' and 'reasoning'."
                )
            else:
                user_prompt = (
                    f"Database Schema:\n{self.schema_str}\n\n"
                    f"User Question: {user_query}\n\n"
                    f"Previous Failed SQL: {sql_query}\n"
                    f"Execution Error: {execution_output['error']}\n\n"
                    "Fix the SQL query and return a new JSON object with 'sql_query' and 'reasoning'."
                )

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                max_tokens=400,
                response_format={"type": "json_object"}
            )

            usage = response.usage
            if usage:
                total_tokens_est += usage.total_tokens

            content = response.choices[0].message.content
            try:
                parsed_json = json.loads(content)
                sql_query = parsed_json.get("sql_query")
            except Exception:
                sql_query = content.strip()

            execution_output = execute_sql_safely(sql_query)

            if execution_output["success"]:
                break

        if not execution_output or not execution_output.get("success"):
            return AgentExecutionResult(
                user_query=user_query,
                generated_sql=sql_query,
                execution_success=False,
                error_message=execution_output.get("error") if execution_output else "Max retries exceeded.",
                tokens_used_estimate=total_tokens_est
            )

        summary_prompt = (
            f"User Question: {user_query}\n"
            f"SQL Used: {sql_query}\n"
            f"Query Results: {json.dumps(execution_output['data'])} \n\n"
            "Provide a concise, professional executive summary with 2-3 key bullet points answering the user's question."
        )

        summary_response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0.3,
            max_tokens=300
        )

        if summary_response.usage:
            total_tokens_est += summary_response.usage.total_tokens

        executive_summary = summary_response.choices[0].message.content

        return AgentExecutionResult(
            user_query=user_query,
            generated_sql=sql_query,
            execution_success=True,
            raw_results=execution_output['data'],
            executive_summary=executive_summary,
            tokens_used_estimate=total_tokens_est
        )
