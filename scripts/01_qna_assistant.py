import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_assistant_id():
    """Load the assistant ID from file"""
    try:
        with open("assistant_id.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("Assistant ID not found. Please run 00_bootstrap.py first.")
        return None

def ask_question(assistant_id, question):
    """Ask a question to the assistant and stream the response"""
    try:
        # Create a thread
        thread = client.beta.threads.create()
        
        # Add message to thread
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question
        )
        
        # Create and stream the run
        with client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=assistant_id
        ) as stream:
            print(f"\nQuestion: {question}")
            print("Answer:")
            
            for event in stream:
                if event.event == 'thread.message.delta':
                    if event.data.delta.content:
                        for content_block in event.data.delta.content:
                            if content_block.type == 'text':
                                print(content_block.text.value, end='', flush=True)
        
        # Get final messages to check for citations
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        latest_message = messages.data[0]
        
        print("\n\nCitations:")
        if hasattr(latest_message.content[0], 'text') and hasattr(latest_message.content[0].text, 'annotations'):
            annotations = latest_message.content[0].text.annotations
            if annotations:
                for annotation in annotations:
                    print(f"- {annotation.text}: {annotation.file_citation.file_id if hasattr(annotation, 'file_citation') else 'No file citation'}")
            else:
                print("No citations found.")
        else:
            print("No citations available.")
            
        print("-" * 50)
        
    except Exception as e:
        print(f"Error asking question: {e}")

def main():
    assistant_id = load_assistant_id()
    if not assistant_id:
        return
    
    # Test questions
    test_questions = [
         "Define narcissism in psychological terms.",
        "What is pathological narcissism and how does it differ from healthy narcissism?"
        "Compare narcissistic personality disorder (NPD) with pathological narcissism."
        "How is pathological narcissism different from grandiose narcissism?"
        "What are the main traits of pathological narcissism?"
        "List the behavioral patterns commonly associated with narcissistic individuals."
        "What are some key psychological theories explaining the development of narcissism?"
        "How does pathological narcissism affect relationships?"
        "What is the impact of narcissism on emotional regulation and empathy?"
        "What treatment approaches are effective for pathological narcissism?"

    ]
    
    for question in test_questions:
        ask_question(assistant_id, question)
    
    # Interactive mode
    print("\nEnter your questions (type 'quit' to exit):")
    while True:
        question = input("\n> ").strip()
        if question.lower() in ['quit', 'exit', 'q']:
            break
        if question:
            ask_question(assistant_id, question)

if __name__ == "__main__":
    main()