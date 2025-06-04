import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_assistant():
    """Create or reuse an assistant with file_search capability"""
    try:
        # Create the assistant
        assistant = client.assistants.create(
            name="Study Q&A Assistant",
            instructions=(
                "You are a helpful tutor. "
                "Use the knowledge in the attached files to answer questions. "
                "Cite sources where possible."
            ),
            model="gpt-4o-mini",
            tools=[{"type": "file_search"}]
        )
        
        print(f"Assistant created with ID: {assistant.id}")
        
        # Upload PDF file
        pdf_path = "data/calculus_basics.pdf"
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as file:
                uploaded_file = client.files.create(
                    purpose="assistants",
                    file=file
                )
            
            # Create vector store and add file
            vector_store = client.beta.vector_stores.create(
                name="Study Materials"
            )
            
            client.beta.vector_stores.files.create(
                vector_store_id=vector_store.id,
                file_id=uploaded_file.id
            )
            
            # Update assistant with vector store
            client.assistants.update(
                assistant.id,
                tool_resources={
                    "file_search": {
                        "vector_store_ids": [vector_store.id]
                    }
                }
            )
            
            print(f"File uploaded and attached: {uploaded_file.id}")
        else:
            print(f"Warning: {pdf_path} not found. Please add your PDF to the data/ folder.")
        
        return assistant.id
        
    except Exception as e:
        print(f"Error creating assistant: {e}")
        return None

if __name__ == "__main__":
    assistant_id = create_assistant()
    if assistant_id:
        # Save assistant ID for reuse
        with open("assistant_id.txt", "w") as f:
            f.write(assistant_id)
        print("Bootstrap complete! Assistant ID saved to assistant_id.txt")