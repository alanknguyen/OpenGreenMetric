.PHONY: install test api dashboard gifs figures all clean

install:
	pip install -e ".[all]"

test:
	pytest tests/ -v

api:
	uvicorn api.main:app --reload --port 8000

dashboard:
	streamlit run streamlit_app.py

gifs:
	python -m viz.gif_monte_carlo
	python -m viz.gif_clustering
	python -m viz.gif_tornado
	python -m viz.gif_waterfall
	python -m viz.gif_material_swap
	python -m viz.gif_world_map
	python -m viz.gif_sankey
	python -m viz.gif_lifecycle

figures:
	python -m analysis.eda
	python -m analysis.clustering
	python -m analysis.regression
	python -m analysis.uncertainty
	python -m analysis.sensitivity
	python -m analysis.geospatial

all: install test gifs figures

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	rm -rf build/ dist/ *.egg-info/
