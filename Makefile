.PHONY: .help
help:
	@echo "clean - remove all artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "lint - check style with flake8"
	@echo "qa - run linters and test coverage"
	@echo "qa-all - run QA plus tox and packaging"
	@echo "release - package and upload a release"
	@echo "sdist - package"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "test-release - upload a release to the PyPI test server"

.PHONY: clean
clean: clean-build clean-pyc clean-test

.PHONY: qa
qa: lint coverage

.PHONY: qa-all
qa-all: qa sdist test-all

.PHONY: clean-build
clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

.PHONY: clean-pyc
clean-pyc:
	find . \( -name \*.pyc -o -name \*.pyo -o -name __pycache__ \) -delete
	find . -name '*~' -delete

.PHONY: clean-test
clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

.PHONY: lint
lint:
	flake8 .

.PHONY: test
test:
	./runtests.py

.PHONY: test-all
test-all:
	tox --skip-missing-interpreters

.PHONY: coverage-console
coverage-console:
	coverage erase
	coverage run ./runtests.py
	coverage report -m

.PHONY: coverage
coverage: coverage-console
	coverage html
	open htmlcov/index.html

.PHONY: release
release: sdist
	twine upload dist/*
	python -m webbrowser -n https://pypi.python.org/pypi/django-pylibmc

.PHONY: test-release
# Add [test] section to ~/.pypirc, https://test.pypi.org/legacy/
test-release: sdist
	twine upload --repository test dist/*
	python -m webbrowser -n https://testpypi.python.org/pypi/django-pylibmc

.PHONY: sdist
sdist: clean
	python setup.py sdist bdist_wheel
	ls -l dist
	check-manifest
	pyroma dist/`ls -t dist | grep tar.gz | head -n1`
