# RAC

Core DSL parser, compiler, and executor for encoding tax and benefit law.

## What belongs here

- `src/rac/ast.py` - AST nodes
- `src/rac/parser.py` - Lexer and parser
- `src/rac/compiler.py` - Temporal resolution, dependency analysis
- `src/rac/executor.py` - Evaluate IR against data
- `src/rac/schema.py` - Entity/field definitions
- `tests/` - Unit tests

## What does not belong here

- `.rac` files with real statute encodings (those go in rac-us, rac-uk)
- `parameters.yaml` with real values

## Commands

```bash
uv pip install -e .
pytest tests/ -v
```

## Related repos

- **rac-us** - US statute encodings
- **rac-uk** - UK statute encodings
