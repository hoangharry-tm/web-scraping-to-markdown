.PHONY: run firecrawl data_processor

all:
	@python3 firecrawl.py
	@python3 data_processor.py

run:
	@python3 main.py

firecrawl:
	@python3 firecrawl.py

missing_files:
	@python3 ./src/missing_files.py

selenium:
	@python3 ./src/selenium_data.py

data_processor:
	@python3 ./src/data_processor.py
