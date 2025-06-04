import pytest
from pydantic import ValidationError
from scripts.notes_02_generate_notes import Note, NotesResponse

def test_valid_note():
    """Test that a valid note passes validation"""
    note_data = {
        "id": 1,
        "heading": "Mean Value Theorem",
        "summary": "States that for a continuous function on a closed interval, there exists a point where the derivative equals the average rate of change.",
        "page_ref": 42
    }
    note = Note(**note_data)
    assert note.id == 1
    assert note.heading == "Mean Value Theorem"
    assert len(note.summary) <= 150
    assert note.page_ref == 42

def test_invalid_note_id():
    """Test that invalid note IDs fail validation"""
    with pytest.raises(ValidationError):
        Note(id=0, heading="Test", summary="Test summary")
    
    with pytest.raises(ValidationError):
        Note(id=11, heading="Test", summary="Test summary")

def test_summary_too_long():
    """Test that summaries over 150 characters fail validation"""
    long_summary = "a" * 151
    with pytest.raises(ValidationError):
        Note(id=1, heading="Test", summary=long_summary)

def test_notes_response():
    """Test that NotesResponse validates correctly"""
    notes_data = [
        {"id": i, "heading": f"Concept {i}", "summary": f"Summary {i}"}
        for i in range(1, 11)
    ]
    
    response = NotesResponse(notes=notes_data)
    assert len(response.notes) == 10

def test_notes_response_wrong_count():
    """Test that NotesResponse fails with wrong number of notes"""
    notes_data = [
        {"id": 1, "heading": "Concept 1", "summary": "Summary 1"}
    ]
    
    with pytest.raises(ValidationError):
        NotesResponse(notes=notes_data)