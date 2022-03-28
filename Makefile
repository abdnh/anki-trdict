.PHONY: all forms zip clean format check ankiweb run
all: ankiweb zip

zip:
	python -m ankibuild --type package --install --qt all --noconsts

ankiweb:
	python -m ankibuild --type ankiweb --install --qt all --noconsts

run: zip
	python -m ankirun

src/vendor/tdk.py:
	mkdir -p src/vendor
	curl https://raw.githubusercontent.com/abdnh/tdk/master/tdk.py -o $@

format:
	python -m black src/

check:
	python -m mypy src/

clean:
	rm -rf build/
