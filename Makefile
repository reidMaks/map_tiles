.PHONY: test coverage

test:
pytest -q

coverage:
pytest --cov=map_generator --cov-report=term-missing
