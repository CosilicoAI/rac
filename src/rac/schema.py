"""Entity schema definitions for RAC.

Schemas define the structure of input data: entity types, their fields,
and relationships between them (foreign keys).
"""

from pydantic import BaseModel


class Field(BaseModel):
    """A field on an entity."""

    name: str
    dtype: str  # int, float, str, bool
    default: object = None


class Relation(BaseModel):
    """A relationship to another entity."""

    name: str
    target: str  # target entity name
    many: bool = False  # True for one-to-many (reverse relation)


class Entity(BaseModel):
    """An entity type in the schema."""

    name: str
    fields: dict[str, Field] = {}
    relations: dict[str, Relation] = {}


class Schema(BaseModel):
    """Complete schema for a ruleset."""

    entities: dict[str, Entity] = {}

    def add_entity(self, entity: Entity) -> None:
        self.entities[entity.name] = entity

    def validate_data(self, data: dict[str, list[dict]]) -> list[str]:
        """Validate input data against schema. Returns list of errors."""
        errors = []

        for entity_name, rows in data.items():
            if entity_name not in self.entities:
                errors.append(f"unknown entity: {entity_name}")
                continue

            entity = self.entities[entity_name]
            for i, row in enumerate(rows):
                if "id" not in row:
                    errors.append(f"{entity_name}[{i}]: missing 'id' field")

                for field_name, fld in entity.fields.items():
                    if field_name not in row and fld.default is None:
                        errors.append(f"{entity_name}[{i}]: missing field '{field_name}'")

                for rel_name, rel in entity.relations.items():
                    if not rel.many and rel_name not in row:
                        errors.append(f"{entity_name}[{i}]: missing relation '{rel_name}'")

        return errors
