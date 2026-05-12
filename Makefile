.PHONY: test run

test:
	python -m unittest discover -v

run-cashflow:
	pip install -r services/cashflow/requirements.txt
	uvicorn services.cashflow.src.main:app --reload --port 8001
