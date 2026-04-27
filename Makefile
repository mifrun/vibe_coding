.PHONY: install check env python agents add add-dev

install:
	poetry install

check:
	poetry check

env:
	poetry env info

python:
	poetry run python --version

agents:
	@test -n "$(task)" || (echo 'Usage: make agents task="your task"' && exit 1)
	poetry run python agents_runner.py "$(task)"

add:
	poetry add $(pkg)

add-dev:
	poetry add --group dev $(pkg)
