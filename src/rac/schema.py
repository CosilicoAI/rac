"""Entity schema and data model for RAC.

Handles relational data with primary keys, foreign keys, and reverse relations.
Data comes from databases/APIs with entity tables linked by IDs.
"""

from typing import Any

from pydantic import BaseModel, model_validator


class Field(BaseModel):
    """A field on an entity."""

    name: str
    dtype: str  # int, float, str, bool, date
    nullable: bool = False
    default: Any = None


class ForeignKey(BaseModel):
    """A foreign key relationship to another entity."""

    name: str  # field name on this entity
    target: str  # target entity name
    target_field: str = "id"  # field on target (usually primary key)


class ReverseRelation(BaseModel):
    """A reverse relation (one-to-many) from another entity."""

    name: str  # accessor name on this entity
    source: str  # source entity name
    source_field: str  # field on source entity pointing to this


class Entity(BaseModel):
    """An entity type in the schema."""

    name: str
    primary_key: str = "id"
    fields: dict[str, Field] = {}
    foreign_keys: dict[str, ForeignKey] = {}
    reverse_relations: dict[str, ReverseRelation] = {}


class Schema(BaseModel):
    """Complete schema for a ruleset."""

    entities: dict[str, Entity] = {}

    def add_entity(self, entity: Entity) -> None:
        self.entities[entity.name] = entity

    def infer_reverse_relations(self) -> None:
        """Auto-generate reverse relations from foreign keys."""
        for entity_name, entity in self.entities.items():
            for fk_name, fk in entity.foreign_keys.items():
                if fk.target in self.entities:
                    target = self.entities[fk.target]
                    # Add reverse relation if not already defined
                    reverse_name = f"{entity_name}s"  # simple pluralisation
                    if reverse_name not in target.reverse_relations:
                        target.reverse_relations[reverse_name] = ReverseRelation(
                            name=reverse_name,
                            source=entity_name,
                            source_field=fk_name,
                        )


class Data(BaseModel):
    """Input data: entity tables with rows."""

    tables: dict[str, list[dict[str, Any]]]  # entity_name -> rows
    _index: dict[str, dict[Any, dict]] = {}  # entity -> pk_value -> row

    @model_validator(mode="after")
    def build_index(self) -> "Data":
        """Build primary key index for fast lookups."""
        object.__setattr__(self, "_index", {})
        for entity_name, rows in self.tables.items():
            self._index[entity_name] = {}
            for row in rows:
                pk = row.get("id")
                if pk is not None:
                    self._index[entity_name][pk] = row
        return self

    def get_row(self, entity: str, pk: Any) -> dict | None:
        """Get a row by primary key."""
        return self._index.get(entity, {}).get(pk)

    def get_rows(self, entity: str) -> list[dict]:
        """Get all rows for an entity."""
        return self.tables.get(entity, [])

    def get_related(self, entity: str, fk_field: str, fk_value: Any) -> list[dict]:
        """Get rows where fk_field == fk_value (for reverse relations)."""
        return [
            row for row in self.tables.get(entity, [])
            if row.get(fk_field) == fk_value
        ]


def validate_data(schema: Schema, data: Data) -> list[str]:
    """Validate data against schema. Returns list of errors."""
    errors = []

    for entity_name, rows in data.tables.items():
        if entity_name not in schema.entities:
            errors.append(f"unknown entity: {entity_name}")
            continue

        entity = schema.entities[entity_name]

        for i, row in enumerate(rows):
            # Check primary key
            if entity.primary_key not in row:
                errors.append(f"{entity_name}[{i}]: missing primary key '{entity.primary_key}'")

            # Check required fields
            for field_name, field in entity.fields.items():
                if field_name not in row and not field.nullable and field.default is None:
                    errors.append(f"{entity_name}[{i}]: missing required field '{field_name}'")

            # Check foreign keys exist
            for fk_name, fk in entity.foreign_keys.items():
                if fk_name in row:
                    fk_value = row[fk_name]
                    if fk_value is not None and data.get_row(fk.target, fk_value) is None:
                        errors.append(
                            f"{entity_name}[{i}]: foreign key '{fk_name}' references "
                            f"non-existent {fk.target} with id={fk_value}"
                        )

    return errors
