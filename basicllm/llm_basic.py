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

    About the Response Object:
        The API returns a Message object with:
        - id:          Unique message identifier
        - content:     List of content blocks (usually text)
        - model:       The exact model version used (e.g. claude-sonnet-4-6-20250514)
        - role:        Always 'assistant' for Claude responses
        - stop_reason: Why it stopped ('end_turn', 'max_tokens', etc.)
        - usage:       Token counts (input_tokens, output_tokens)
                       Used for cost calculation: output_tokens cost 5× more
    """
    # Initialize the Anthropic client with API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set. Please add it to .env file.")

    client = Anthropic(api_key=api_key)

    # Call the Claude LLM model
    # This returns a Message object with all response metadata
    response = client.messages.create(
        model="claude-sonnet-4-6",  # Latest Claude Sonnet 4.6 model
        max_tokens=500,             # Hard ceiling — response cuts off if it exceeds this
        messages=[
            {"role": "user", "content": question}
        ]
    )

    # response structure:
    # {
    #   'id': 'msg_01P2Dwnjd3t2sGvk9fJGBssy',
    #   'content': [TextBlock(text='...', type='text')],
    #   'model': 'claude-sonnet-4-6-20250514',
    #   'role': 'assistant',
    #   'stop_reason': 'end_turn',
    #   'usage': Usage(
    #       input_tokens=45,
    #       output_tokens=128,
    #       cache_creation_input_tokens=0,
    #       cache_read_input_tokens=0
    #   )
    # }

    # Extract and return just the text response
    # response.content[0] is a TextBlock object
    # .text is the actual string response from Claude
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
