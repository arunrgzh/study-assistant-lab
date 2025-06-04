import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Note(BaseModel):
    id: int = Field(..., ge=1, le=10, description="Note ID from 1 to 10")
    heading: str = Field(..., example="Mean Value Theorem", description="Concise heading for the note")
    summary: str = Field(..., max_length=150, description="Brief summary of the concept")
    page_ref: Optional[int] = Field(None, description="Page number in source PDF")

class NotesResponse(BaseModel):
    notes: List[Note] = Field(..., min_items=10, max_items=10, description="Exactly 10 study notes")

def load_assistant_id():
    """Load the assistant ID from file"""
    try:
        with open("assistant_id.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("Assistant ID not found. Please run 00_bootstrap.py first.")
        return None

def generate_notes(assistant_id):
    """Generate 10 exam notes using structured output"""
    try:
        # Create a thread
        thread = client.beta.threads.create()
        
        # Add message requesting notes generation
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=(
                "Generate exactly 10 unique study notes from the uploaded materials "
                "that will help prepare for an exam. Each note should have a clear heading, "
                "concise summary (max 150 chars), and page reference if available. "
                "Cover the most important concepts comprehensively."
            )
        )
        
        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )
        
        # Wait for completion
        while run.status in ['queued', 'in_progress']:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
        
        if run.status == 'completed':
            # Get the response
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            assistant_response = messages.data[0].content[0].text.value
            
            # Now use structured output to format the response
            system_prompt = (
                "You are a study summarizer. "
                "Convert the provided study material into exactly 10 unique notes "
                "that will help prepare for the exam. "
                "Respond only with valid JSON matching the required schema."
            )
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Convert this content into 10 structured notes: {assistant_response}"}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse and validate the response
            data = json.loads(response.choices[0].message.content)
            
            # Ensure we have the right structure
            if "notes" not in data:
                data = {"notes": data if isinstance(data, list) else [data]}
            
            # Validate with Pydantic
            notes_response = NotesResponse(**data)
            return notes_response.notes
            
        else:
            print(f"Run failed with status: {run.status}")
            return None
            
    except Exception as e:
        print(f"Error generating notes: {e}")
        return None

def save_notes(notes, filename="exam_notes.json"):
    """Save notes to JSON file"""
    try:
        notes_dict = {"notes": [note.model_dump() for note in notes]}
        with open(filename, "w") as f:
            json.dump(notes_dict, f, indent=2)
        print(f"Notes saved to {filename}")
    except Exception as e:
        print(f"Error saving notes: {e}")

def print_notes(notes):
    """Print notes in a readable format"""
    print("\n" + "="*60)
    print("EXAM REVISION NOTES")
    print("="*60)
    
    for note in notes:
        print(f"\n{note.id}. {note.heading}")
        print("-" * len(f"{note.id}. {note.heading}"))
        print(f"Summary: {note.summary}")
        if note.page_ref:
            print(f"Page Reference: {note.page_ref}")
        print()

def main():
    assistant_id = load_assistant_id()
    if not assistant_id:
        return
    
    print("Generating 10 exam notes...")
    notes = generate_notes(assistant_id)
    
    if notes:
        print_notes(notes)
        save_notes(notes)
        print(f"\nGenerated {len(notes)} notes successfully!")
    else:
        print("Failed to generate notes.")

if __name__ == "__main__":
    main()