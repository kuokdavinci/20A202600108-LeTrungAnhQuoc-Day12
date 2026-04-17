import time

def ask(question: str) -> str:
    """Mock LLM response for testing purposes."""
    # Simulate a small delay
    time.sleep(0.5)
    return f"[Mock LLM] You asked: '{question}'. This is a production-ready response!"
