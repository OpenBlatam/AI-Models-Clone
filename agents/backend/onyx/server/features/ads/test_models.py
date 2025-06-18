import pytest
from uuid6 import UUID, uuid7
from agents.backend.onyx.server.features.ads.models import Ad
from agents.backend.onyx.server.features.ads.schemas import AdCreate, AdRead

def test_ad_valid():
    ad = Ad(title="AdTitle", content="Some content", metadata={"type": "banner"})
    assert isinstance(ad.id, UUID)
    assert ad.title == "AdTitle"
    assert ad.content == "Some content"
    assert ad.metadata == {"type": "banner"}

def test_ad_empty_title_raises():
    with pytest.raises(ValueError):
        Ad(title=" ", content="Content", metadata={})

def test_ad_empty_content_raises():
    with pytest.raises(ValueError):
        Ad(title="Title", content=" ", metadata={})

def test_ad_metadata_not_dict():
    with pytest.raises(ValueError):
        Ad(title="Title", content="Content", metadata=[1,2,3])

def test_ad_serialization():
    ad = Ad(title="AdTitle", content="Content", metadata={})
    data = ad.model_dump_json()
    assert '"title":"AdTitle"' in data

def test_ad_create_valid():
    schema = AdCreate(title="AdTitle", content="Content", metadata={})
    assert schema.title == "AdTitle"
    assert schema.content == "Content"

def test_ad_create_invalid_title():
    with pytest.raises(ValueError):
        AdCreate(title=" ", content="Content", metadata={})

def test_ad_create_invalid_content():
    with pytest.raises(ValueError):
        AdCreate(title="Title", content=" ", metadata={})

def test_ad_create_metadata_not_dict():
    with pytest.raises(ValueError):
        AdCreate(title="Title", content="Content", metadata=[1,2,3])

def test_ad_read_valid():
    schema = AdRead(id=uuid7(), title="AdTitle", content="Content", metadata={})
    assert schema.title == "AdTitle"
    assert schema.content == "Content"
    assert isinstance(schema.id, UUID) 