"""
Basic LLM Connection and Query Example
This script demonstrates how to connect to Claude LLM and ask a simple question.
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables from .env file
load_dotenv()

def call_llm(question: str) -> str:
    """
    Call the Claude LLM model with a question and return the response.

    Args:
        question: The question to ask the LLM

    Returns:
        The LLM's response as a string
    """
    # Initialize the Anthropic client with API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set. Please add it to .env file.")

    client = Anthropic(api_key=api_key)

    # Call the Claude LLM model
    response = client.messages.create(
        model="claude-sonnet-4-6",  # Latest Claude Sonnet 4.6 model
        max_tokens=500,
        messages=[
            {"role": "user", "content": question}
        ]
    )

    # Extract and return the response text
    return response.content[0].text


def main():
    """Main function to demonstrate LLM usage."""

    print("=" * 60)
    print("Basic LLM Connection Example")
    print("=" * 60)

    # Get question from user input
    question = input("Enter your question: ")

    print(f"\nQuestion: {question}\n")

    try:
        # Call the LLM
        answer = call_llm(question)

        print("Response from LLM:")
        print("-" * 60)
        print(answer)
        print("-" * 60)

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
