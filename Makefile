-include Makefile.override.mk

.PHONY: lint
lint:
	uv run ruff check .

.PHONY: format
format:
	uv run ruff format .

.PHONY: test
test:
	uv run pytest