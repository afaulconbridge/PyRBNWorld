
.PHONY: all test pylint benchmark doc dochtml doclatex setup

help:
	@echo "The following make targets are avaliable:"
	@echo "  all        Run clean, test, and doc"
	@echo "  test       Run tests and test coverage"
	@echo "  pylint     Run pylint for code quality"
	@echo "  benchmark  Performance of different variants"
	@echo "  doc        Generate documentation (HTML + LaTeX)"
	@echo "  dochtml    Generate documentation in HTML"
	@echo "  doclatex   Generate documentation in LaTeX"
	@echo "  setup      Try to install / update required modules"

all: doc test

test:
	coverage run rununittest.py
	coverage report
	coverage xml

pylint:
	pylint --rcfile=pylint.rc -f parseable rbnworld > pylint.txt

benchmark:
	python tst/bench.py

doc: dochtml doclatex

dochtml:
	python doc/src/generate_modules.py -d doc/src/ -s rst -f -m 10 rbnworld
	sphinx-build -b html -n doc/src doc/html

doclatex:
	python doc/src/generate_modules.py -d doc/src/ -s rst -f -m 10 rbnworld
	sphinx-build -b latex -n doc/src doc/latex
	pdflatex -output-directory doc/latex  doc/latex/AChemKit > /dev/null
	pdflatex -output-directory doc/latex  doc/latex/AChemKit > /dev/null
	pdflatex -output-directory doc/latex  doc/latex/AChemKit > /dev/null

setup: 
	sudo apt-get install python-dev python-setuptools 
	#sudo apt-get install texlive-full #needed to build pdf docs, but big so not done by defualt
	sudo easy_install -U coverage pylint sphinx
