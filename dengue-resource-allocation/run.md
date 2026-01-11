python -m venv venv

\\venv\Scripts\activate 

pip install -r requirements.txt

python ml/preprocess.py | python ml/preprocess_windows.py

python fix_population_data.py

python train_all_models.py

python ml/predict.py

\\ python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload