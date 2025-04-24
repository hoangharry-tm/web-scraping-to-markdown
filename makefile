.PHONY: run firecrawl data_processor

run:
	@python3 main.py

firecrawl:
	@python3 firecrawl.py

missing_files:
	@python3 ./src/missing_files.py

data_processor:
	@python3 ./src/data_processor.py
