# Fraud Detection Web App — README

This document describes the repository contents, how to run the Streamlit application locally and on Streamlit Community Cloud, model retraining guidance, and operational notes for maintaining a production-ready fraud detection service.

If you removed the `Dockerfile` and plan to deploy directly from GitHub to Streamlit Community Cloud, this README focuses on that workflow and on reproducibility.

## Repository contents

- `fraud_detection.py` — Streamlit application. Loads `fraud_detection_pipeline.pkl` at runtime and provides an interactive UI to score single transactions.
- `analysis_model.ipynb` — Notebook containing EDA, feature engineering and model training/comparison logic. The notebook includes a final cell to persist the selected pipeline using `joblib.dump`.
- `fraud_detection_pipeline.pkl` — Serialized scikit-learn pipeline (preprocessing + estimator). Keep it synchronized with the runtime environment used by the app.
- `Fraud_Detection_DataSet.csv` — Source data used in the notebook (research/training).
- `requirements.txt` — Pinned dependencies for reproducibility. The Streamlit Cloud build uses this file to install packages.

## Professional quickstart — local development

1. Clone the repository (or open this workspace).

2. Create a reproducible Python environment and install pinned dependencies. Example (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. Launch the Streamlit app locally:

```powershell
streamlit run fraud_detection.py
```

4. Open the URL printed by Streamlit (typically `http://localhost:8501`) and interact with the UI.

Notes for developers

- Use the same `requirements.txt` to build the runtime where you train/serialize the pipeline to prevent pickle incompatibilities.
- The app now lazy-loads the pipeline at prediction time; any model-load errors will be surfaced in the Streamlit UI and in the server logs.

## Deploying to Streamlit Community Cloud (GitHub → Streamlit)

Streamlit Community Cloud automatically installs packages from `requirements.txt` and runs the specified app file.

1. Push this repository to a GitHub repository (private or public).
2. In Streamlit Community Cloud (https://share.streamlit.io), create a new app and point it to the GitHub repo, branch and `fraud_detection.py` as the entry point.
3. Set any required secrets (if you plan to load the model from external storage) using the Streamlit Cloud secrets manager.

Operational notes

- If `fraud_detection_pipeline.pkl` is large or you prefer not to commit it to the repo, host the model artifact in secure object storage (S3, Azure Blob, etc.) and update `fraud_detection.py` to download and cache the model at startup using a signed URL or authenticated client.
- When deploying from GitHub, verify `requirements.txt` matches the packages used to train the model. Mismatched versions are the most common cause of runtime errors when unpickling the pipeline.

## Retraining and publishing a new model

Best-practice workflow:

1. Create or switch to a reproducible environment that uses the same package versions listed in `requirements.txt`.
2. Open `analysis_model.ipynb` and run the notebook cells (EDA → preprocessing → model comparison).
3. The notebook contains a model-selection cell that chooses the best candidate by fraud-class F1 and writes `fraud_detection_pipeline.pkl` using `joblib.dump`.
4. Validate the saved pipeline locally by running the Streamlit app against a small test sample.
5. Commit the updated `fraud_detection_pipeline.pkl` and push to GitHub, or upload the artifact to your model store and update the app to download it at startup.

Notes on serialization and compatibility

- Always pin the versions of `scikit-learn`, `pandas`, `numpy`, and `joblib` used for training and runtime. If you retrain using newer versions, update `requirements.txt` and redeploy.
- If you are concerned about binary artifacts in Git, consider storing the model in object storage and using CI/CD to fetch the artifact during deployment.

## Evaluation & metrics (recommended)

- Primary focus: fraud-class metrics due to extreme class imbalance (precision, recall, F1, PR-AUC).
- Supplement with business metrics: precision@k, expected cost (false positives vs false negatives), and alerting throughput.

## Production considerations

- Monitoring: log prediction requests, prediction latency, and outcome labels (if ground truth becomes available) to monitor model drift.
- Explainability: attach SHAP or similar explainability to your model pipeline for investigator workflows.
- Retraining cadence: schedule retraining when model performance degrades or when new labeled data accumulates.

## Troubleshooting

- App shows blank page: open the Streamlit server terminal and browser console. The app surfaces model-load errors in the UI; check for pickle/version incompatibilities.
- `ModuleNotFoundError` on deployment: ensure `requirements.txt` includes the missing package and push changes to GitHub.

## Contact & next steps

If you want, I can:

- Run the notebook's model-comparison locally, evaluate the candidates on fraud-class metrics, and save the best pipeline.
- Add a small CI step (GitHub Actions) that validates that the app boots and the saved pipeline can be loaded (useful for preventing broken deployments).

Please tell me which of these you'd like me to do next and I will proceed.

Docker registry push & run (example for Docker Hub)
-------------------------------------------------

1. Build the Docker image locally:

   docker build -t <dockerhub-username>/fraud-app:latest .

2. Log in and push:

   docker login
   docker push <dockerhub-username>/fraud-app:latest

3. Pull & run on any host with Docker:

   docker pull <dockerhub-username>/fraud-app:latest
   docker run -p 8501:8501 <dockerhub-username>/fraud-app:latest

Model hosting (recommended for large models)
-------------------------------------------

- Upload `fraud_detection_pipeline.pkl` to S3/Azure Blob and make it accessible via a signed URL, or require authentication via secrets.
- Modify `fraud_detection.py` to download the model at startup and cache it locally (or stream it) so you don't commit the binary to Git.

If you'd like, tell me which deployment target you prefer (Streamlit Cloud, Docker Hub, Azure, AWS) and I will:
- Provide step-by-step commands tailored to that provider.
- Optionally implement model-from-URL code in `fraud_detection.py` and demonstrate how to set secrets or environment variables for credentials.
