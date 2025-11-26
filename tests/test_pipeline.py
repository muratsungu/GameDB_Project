"""Basic pipeline tests."""
import pandas as pd
import pytest

from etl.dimensions import DimensionBuilder
from etl.bridges import BridgeBuilder
from etl.fact import FactBuilder


@pytest.fixture
def sample_raw_data():
    """Sample raw game data for testing."""
    return pd.DataFrame([
        {
            "id": 1,
            "name": "Test Game",
            "slug": "test-game",
            "released": "2024-01-15",
            "updated": "2024-01-20",
            "rating": 4.5,
            "ratings_count": 100,
            "playtime": 10,
            "platforms": [{"platform": {"id": 1, "name": "PC", "slug": "pc"}}],
            "stores": [{"store": {"id": 1, "name": "Steam", "slug": "steam"}}],
            "genres": [{"id": 1, "name": "Action", "slug": "action"}],
            "tags": [{"id": 1, "name": "Singleplayer", "slug": "singleplayer"}],
            "esrb_rating": {"id": 1, "name": "Everyone", "slug": "everyone"},
        }
    ])


def test_dimension_builder(sample_raw_data):
    """Test dimension table building."""
    builder = DimensionBuilder(sample_raw_data)
    dimensions = builder.build_all()

    assert "dim_platform" in dimensions
    assert "dim_store" in dimensions
    assert "dim_genre" in dimensions
    assert "dim_tag" in dimensions
    assert "dim_esrb_rating" in dimensions
    assert "dim_date" in dimensions

    assert len(dimensions["dim_platform"]) == 1
    assert dimensions["dim_platform"].iloc[0]["name"] == "PC"


def test_bridge_builder(sample_raw_data):
    """Test bridge table building."""
    dim_builder = DimensionBuilder(sample_raw_data)
    dimensions = dim_builder.build_all()

    bridge_builder = BridgeBuilder(sample_raw_data, dimensions)
    bridges = bridge_builder.build_all()

    assert "bridge_game_platform" in bridges
    assert "bridge_game_store" in bridges
    assert "bridge_game_genre" in bridges
    assert "bridge_game_tag" in bridges

    assert len(bridges["bridge_game_platform"]) == 1
    assert bridges["bridge_game_platform"].iloc[0]["game_id"] == 1


def test_fact_builder(sample_raw_data):
    """Test fact table building."""
    dim_builder = DimensionBuilder(sample_raw_data)
    dimensions = dim_builder.build_all()

    fact_builder = FactBuilder(sample_raw_data, dimensions)
    fact = fact_builder.build()

    assert len(fact) == 1
    assert fact.iloc[0]["game_id"] == 1
    assert fact.iloc[0]["name"] == "Test Game"
    assert fact.iloc[0]["rating"] == 4.5
