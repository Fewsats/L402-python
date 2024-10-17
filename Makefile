install:
	poetry install
test:
	poetry run pytest
release:
	poetry publish --build
deploy:
	poetry publish --build --username __token__ --password ${PYPI_TOKEN}
clean:
	rm -rf venv
