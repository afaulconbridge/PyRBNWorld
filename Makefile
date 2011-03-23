
help:
	@echo "The following make targets are avaliable:"
	@echo "   test       Test code quality and coverage"
	@echo "   benchmark  Performance of different variants"

.PHONEY: test benchmark

test:
	#use nose
	
benchmark:
	python tst/bench.py
