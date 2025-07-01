import pytest
from uuid6 import UUID, uuid7
from agents.backend.onyx.server.features.document_set.models import DocumentSet
from agents.backend.onyx.server.features.document_set.schemas import DocumentSetCreate, DocumentSetRead

def test_document_set_valid():
    ds = DocumentSet(name="Docs", documents=["a.pdf"], metadata={"type": "pdf"})
    assert isinstance(ds.id, UUID)
    assert ds.name == "Docs"
    assert ds.documents == ["a.pdf"]
    assert ds.metadata == {"type": "pdf"}

def test_document_set_empty_name_raises():
    with pytest.raises(ValueError):
        DocumentSet(name=" ", documents=[], metadata={})

def test_document_set_documents_not_list():
    with pytest.raises(ValueError):
        DocumentSet(name="Set", documents="notalist", metadata={})

def test_document_set_metadata_not_dict():
    with pytest.raises(ValueError):
        DocumentSet(name="Set", documents=[], metadata=[1,2,3])

def test_document_set_serialization():
    ds = DocumentSet(name="Set", documents=[], metadata={})
    data = ds.model_dump_json()
    assert '"name":"Set"' in data

def test_document_set_create_valid():
    schema = DocumentSetCreate(name="Docs", documents=["a.pdf"], metadata={"type": "pdf"})
    assert schema.name == "Docs"
    assert schema.documents == ["a.pdf"]

def test_document_set_create_invalid_name():
    with pytest.raises(ValueError):
        DocumentSetCreate(name=" ", documents=[], metadata={})

def test_document_set_read_valid():
    schema = DocumentSetRead(id=uuid7(), name="Set", documents=[], metadata={})
    assert schema.name == "Set"
    assert isinstance(schema.id, UUID) 