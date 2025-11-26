"""Iceberg schema definitions."""
from pyiceberg.schema import Schema
from pyiceberg.types import (
    NestedField,
    IntegerType,
    StringType,
    FloatType,
    BooleanType,
    DateType,
)


def dim_platform_schema() -> Schema:
    return Schema(
        NestedField(1, "platform_id", IntegerType(), required=True),
        NestedField(2, "platform_key", IntegerType(), required=False),
        NestedField(3, "name", StringType(), required=False),
        NestedField(4, "slug", StringType(), required=False),
    )


def dim_store_schema() -> Schema:
    return Schema(
        NestedField(1, "store_id", IntegerType(), required=True),
        NestedField(2, "store_key", IntegerType(), required=False),
        NestedField(3, "name", StringType(), required=False),
        NestedField(4, "slug", StringType(), required=False),
    )


def dim_genre_schema() -> Schema:
    return Schema(
        NestedField(1, "genre_id", IntegerType(), required=True),
        NestedField(2, "genre_key", IntegerType(), required=False),
        NestedField(3, "name", StringType(), required=False),
        NestedField(4, "slug", StringType(), required=False),
    )


def dim_tag_schema() -> Schema:
    return Schema(
        NestedField(1, "tag_id", IntegerType(), required=True),
        NestedField(2, "tag_key", IntegerType(), required=False),
        NestedField(3, "name", StringType(), required=False),
        NestedField(4, "slug", StringType(), required=False),
        NestedField(5, "games_count", IntegerType(), required=False),
    )


def dim_esrb_rating_schema() -> Schema:
    return Schema(
        NestedField(1, "esrb_id", IntegerType(), required=True),
        NestedField(2, "esrb_key", IntegerType(), required=False),
        NestedField(3, "name", StringType(), required=False),
        NestedField(4, "slug", StringType(), required=False),
    )


def dim_date_schema() -> Schema:
    return Schema(
        NestedField(1, "date_id", IntegerType(), required=True),
        NestedField(2, "full_date", DateType(), required=False),
        NestedField(3, "year", IntegerType(), required=False),
        NestedField(4, "quarter", IntegerType(), required=False),
        NestedField(5, "month", IntegerType(), required=False),
        NestedField(6, "day", IntegerType(), required=False),
        NestedField(7, "day_of_week", IntegerType(), required=False),
    )


def fact_games_schema() -> Schema:
    return Schema(
        NestedField(1, "game_id", IntegerType(), required=True),
        NestedField(2, "date_id", IntegerType(), required=False),
        NestedField(3, "esrb_id", IntegerType(), required=False),
        NestedField(4, "slug", StringType(), required=False),
        NestedField(5, "name", StringType(), required=False),
        NestedField(6, "released", StringType(), required=False),
        NestedField(7, "updated", StringType(), required=False),
        NestedField(8, "background_image", StringType(), required=False),
        NestedField(9, "tba", BooleanType(), required=False),
        NestedField(10, "playtime", IntegerType(), required=False),
        NestedField(11, "ratings_count", IntegerType(), required=False),
        NestedField(12, "reviews_count", IntegerType(), required=False),
        NestedField(13, "reviews_text_count", IntegerType(), required=False),
        NestedField(14, "added", IntegerType(), required=False),
        NestedField(15, "suggestions_count", IntegerType(), required=False),
        NestedField(16, "rating", FloatType(), required=False),
        NestedField(17, "rating_top", IntegerType(), required=False),
        NestedField(18, "metacritic", IntegerType(), required=False),
        NestedField(19, "community_rating", FloatType(), required=False),
        NestedField(20, "saturated_color", StringType(), required=False),
        NestedField(21, "dominant_color", StringType(), required=False),
    )


def bridge_schema() -> Schema:
    return Schema(
        NestedField(1, "game_id", IntegerType(), required=True),
        NestedField(2, "dimension_id", IntegerType(), required=True),
    )
