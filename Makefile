install:
	python -m pip install -r requirements.txt

pipeline:
	python -m src.evintel.pipeline

dashboard:
	streamlit run app.py

test:
	pytest -q
