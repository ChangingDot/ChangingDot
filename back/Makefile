########################################################################################################################
# Quality checks
########################################################################################################################

test:
	poetry run pytest tests

format:
	poetry run ruff format . --check

lint:
	poetry run ruff check src tests

fix-lint:
	poetry run ruff check src tests --fix

mypy:
	poetry run mypy src tests

ci:
	make test && make format && make lint && make mypy

########################################################################################################################
# Api
########################################################################################################################

generate-grpc-client:
	poetry run python -m grpc_tools.protoc -I../protos --python_out=./src/core/generated_grpc --pyi_out=./src/core/generated_grpc_types --grpc_python_out=./src/core/generated_grpc ../protos/feedback_server.proto

start-api:
	docker compose up -d
