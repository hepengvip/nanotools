WITH_ENV = env `cat .env 2>/dev/null | xargs`

clean:
	@rm -f dist/* nanotools.egg-info/*
	@rm -f celerybeat-schedule.{bak,dat,dir}
	@rm -rf .pytest_cache htmlcov
	@rm -f .coverage
	@find . -name '*.pyc' -delete
	@find . -name '__pycache__' -delete
	@find . -type d -empty -delete

lint:
	flake8

test:
	# @[ -n "$(VIRTUAL_ENV)" ] || (echo 'out of virtualenv'; exit 1)
	# python manage.py initdb
	coverage erase
	NANOTOOLS_CONFIG_FILE=config/config-example.json coverage run -m --append pytest tests -p no:warnings
	coverage report --omit=*tests*
	coverage html --omit=*tests*

testverbose:
	env PYTEST_ADDOPTS="-s" tox -vvv

dist: clean
	@python3 ./setup.py sdist bdist_wheel
	@rm -rf build/*
