Still in development

# Code style


## Type annotations

- must be annotated: function arguments, variables, return values
- orm classes must be mapped with annotated python types

## Routers

- camel case
- slash at the end of route
- define named parameters
- write summary
- define request model(s)
- define response model with ApplicationResponse
- define status code

## Imports

- divide lib imports from python package imports
- avoid importing everything from package with asterisks
- all modules must be imported in __init__ files
- don't repeat libraries while importing
- remove unused imports before commit


# Run

For run application use:

```shell
docker-compose -f docker-compose.yml -f docker-compose.db.yml up --build -d
```

For run migrations use:

```shell
docker-compose -f docker-compose.yml -f docker-compose.alembic.yml -f docker-compose.db.yml up --build -d
```
