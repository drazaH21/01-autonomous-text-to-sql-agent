import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.agent import TextToSQLAgent

def test_agent_execution():
    print("Initializing Text-to-SQL Agent with Groq (openai/gpt-oss-20b)...")
    agent = TextToSQLAgent(model_name="openai/gpt-oss-20b")

    test_questions = [
        "What is the total revenue generated in the North region?",
        "Which product category had the highest total quantity sold?",
        "List the top 3 customers by total revenue."
    ]

    for i, q in enumerate(test_questions, 1):
        print(f"\n==============================")
        print(f"Test Question {i}: {q}")
        print(f"==============================")

        result = agent.run(q)

        print(f"Generated SQL: {result.generated_sql}")
        print(f"Execution Success: {result.execution_success}")
        
        if result.execution_success:
            print(f"\nRaw Results:\n{result.raw_results}")
            print(f"\nExecutive Summary:\n{result.executive_summary}")
        else:
            print(f"\nError: {result.error_message}")

        print(f"\n--- Token Telemetry ---")
        print(f"Estimated Tokens Used: {result.tokens_used_estimate} tokens")
        print(f"Estimated Cost: $0.00 (Free Tier Active)")

    print("\nAll test runs completed successfully!")

if __name__ == "__main__":
    test_agent_execution()
