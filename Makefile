export PIPENV_VERBOSITY=-1
export PYTHONPATH=./src

run:
	@pipenv run python ./src/project_gamepad/app.py

lint:
	@pipenv run isort .
	@pipenv run black .
