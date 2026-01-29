PKGNAME=yaplotlib

all:
	echo Hello.


test-deploy:
	poetry publish --build -r testpypi
test-install:
	pip install --index-url https://test.pypi.org/simple/ $(PKGNAME)
uninstall:
	-pip uninstall -y $(PKGNAME)
build: README.md
	poetry build
deploy:
	poetry publish --build
check:
	poetry check


docs:
	pdoc -o docs yaplotlib

clean:
	-rm *~
	-rm -rf build dist *.egg-info docs
