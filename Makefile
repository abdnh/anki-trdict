.PHONY: all forms zip clean format check
all: zip

forms: src/form.py
zip: forms TRDict.ankiaddon

src/form.py: designer/dialog.ui
	pyuic5 $^ > $@

TRDict.ankiaddon: $(shell find src/ -type f) tdk
	rm -f $@
	( cd src/; zip -r ../$@ * )

tdk: src/vendor/tdk.py

src/vendor/tdk.py:
	curl https://raw.githubusercontent.com/abdnh/tdk/master/tdk.py -o $@

# Install in test profile
install: zip
	unzip -o TRDict.ankiaddon -d ankiprofile/addons21/TRDict

format:
	python -m black src/

check:
	python -m mypy src/

clean:
	rm -f src/form.py
	rm -f TRDict.ankiaddon
