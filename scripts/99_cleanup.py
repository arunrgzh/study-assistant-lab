import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def cleanup():
    """Clean up created assistants and files"""
    try:
        # Load assistant ID
        assistant_id = None
        if os.path.exists("assistant_id.txt"):
            with open("assistant_id.txt", "r") as f:
                assistant_id = f.read().strip()
        
        if assistant_id:
            # Delete assistant
            client.assistants.delete(assistant_id)
            print(f"Deleted assistant: {assistant_id}")
            
            # Remove assistant ID file
            os.remove("assistant_id.txt")
            print("Removed assistant_id.txt")
        
        # List and delete uploaded files
        files = client.files.list(purpose="assistants")
        for file in files.data:
            client.files.delete(file.id)
            print(f"Deleted file: {file.id}")
        
        # Clean up generated files
        if os.path.exists("exam_notes.json"):
            os.remove("exam_notes.json")
            print("Removed exam_notes.json")
        
        print("Cleanup complete!")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    cleanup()
