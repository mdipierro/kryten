dist:
	python setup.py sdist
deploy:
	#http://guide.python-distribute.org/creation.html
	python setup.py sdist
	python setup.py register
	python setup.py sdist upload