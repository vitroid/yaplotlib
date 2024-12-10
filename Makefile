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


clean:
	-rm *~ 
	-rm -rf build dist *.egg-info
