import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, AsyncMock

from app.main import app
from app.database import Base, get_db, Document

SQLALCHEMY_DATABASE_URL = "sqlite:///./doc_intel.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def init_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_health_check():
    """Test 1: Verify the health endpoint works."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch("app.api.extract_text")
def test_upload_document_success(mock_extract):
    """
    Test 2: Successful document upload.
    """
    mock_extract.return_value = "Invoice Total: $500.00"

    file_content = b"fake_image_bytes_123"
    files = {"file": ("receipt.png", file_content, "image/png")}

    response = client.post("/api/v1/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "receipt.png"
    assert data["message"] == "Processed successfully"
    assert "id" in data

    mock_extract.assert_called_once()

    db = TestingSessionLocal()
    saved_doc = db.query(Document).filter(Document.id == data["id"]).first()
    assert saved_doc is not None
    assert saved_doc.extracted_text == "Invoice Total: $500.00"
    db.close()

@patch("app.api.extract_text")
def test_upload_duplicate_document(mock_extract):
    """
    Test 3: Uploading the exact same file twice.
    """
    mock_extract.return_value = "Sample Text"
    files = {"file": ("duplicate.png", b"same_content_bytes", "image/png")}

    resp1 = client.post("/api/v1/upload", files=files)
    assert resp1.status_code == 200

    resp2 = client.post("/api/v1/upload", files=files)
    assert resp2.status_code == 200
    
    assert resp1.json()["id"] == resp2.json()["id"]
    assert resp2.json()["message"] == "Document already exists"
    
    mock_extract.assert_called_once()

def test_upload_invalid_file_type():
    """Test 4: Uploading a text file should fail."""
    files = {"file": ("notes.txt", b"plain text", "text/plain")}
    response = client.post("/api/v1/upload", files=files)
    assert response.status_code == 400
    assert response.json()["detail"] == "File must be an image."

@patch("app.api.ask_llm", new_callable=AsyncMock)
def test_ask_question(mock_ask_llm):
    """
    Test 5: Asking a question.
    """
    db = TestingSessionLocal()
    doc_id = "test_hash_id"
    doc = Document(
        id=doc_id, 
        filename="test_doc.png", 
        extracted_text="The vendor is Acme Corp."
    )
    db.add(doc)
    db.commit()
    db.close()

    mock_ask_llm.return_value = "The vendor is Acme Corp."

    payload = {"document_id": doc_id, "question": "Who is the vendor?"}
    response = client.post("/api/v1/ask", json=payload)

    assert response.status_code == 200
    assert response.json()["answer"] == "The vendor is Acme Corp."
    
    mock_ask_llm.assert_awaited_once()