python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install poetry
poetry install
pre-commit install
sh scripts/mypy.sh
