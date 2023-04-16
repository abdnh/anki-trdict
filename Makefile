.PHONY: all zip ankiweb fix mypy pylint clean

all: ankiweb zip

zip:
	python -m ankibuild --type package --qt all --exclude user_files/**/ --exclude user_files/*.json

ankiweb:
	python -m ankibuild --type ankiweb --qt all --exclude user_files/**/ --exclude user_files/*.json

src/vendor/tdk.py:
	mkdir -p src/vendor
	curl https://raw.githubusercontent.com/abdnh/tdk/master/tdk.py -o $@

fix:
	python -m black src tests --exclude="forms|vendor"
	python -m isort src tests

mypy:
	python -m mypy src tests

pylint:
	python -m pylint src tests

clean:
	rm -rf build/
