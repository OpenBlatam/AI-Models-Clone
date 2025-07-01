import pytest
from uuid6 import UUID, uuid7
from agents.backend.onyx.server.features.ads.models import Ad
from agents.backend.onyx.server.features.ads.schemas import AdCreate, AdRead
import orjson

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

def test_ad_example():
    ad = Ad.example()
    assert isinstance(ad, Ad)
    assert ad.title
    assert ad.content
    assert isinstance(orjson.loads(ad.to_json()), dict)

def test_ad_random():
    ad = Ad.random()
    assert isinstance(ad, Ad)
    assert ad.title
    assert ad.content

def test_ad_to_json_and_from_json():
    ad = Ad.random()
    data = ad.to_json()
    ad2 = Ad.from_json(data)
    assert ad2.title == ad.title
    assert ad2.content == ad.content

def test_ad_to_training_example_and_from_training_example():
    ad = Ad.random()
    ex = ad.to_training_example()
    ad2 = Ad.from_training_example(ex)
    assert ad2.title == ad.title
    assert ad2.content == ad.content 