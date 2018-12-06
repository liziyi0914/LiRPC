build:
	python setup.py sdist build
	python setup.py bdist_wheel --universal

upload:
	twine upload dist/*

clean:
	rm -rf dist
	rm -rf build
	rm -rf __pycache__
	rm -rf *.egg-info
