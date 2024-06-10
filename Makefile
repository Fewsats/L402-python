install:
	poetry install
test:
	poetry run pytest
deploy:
	poetry publish
clean:
	rm -rf venv
