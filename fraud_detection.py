import os
import traceback
import streamlit as st
import pandas as pd
import joblib

MODEL_PATH = 'fraud_detection_pipeline.pkl'

st.title("Fraud Detection Prediction App")
st.markdown("Please enter the transaction details below and use the predict button")
st.markdown("---")  # divider

transaction_type = st.selectbox("Transaction Type", ['PAYMENT', 'TRANSFER', 'CASH_OUT', 'DEPOSIT'])
amount = st.number_input("Amount", min_value=0.0, value=10000.0)
oldbalanceOrg = st.number_input("Old Balance (Sender)", min_value=0.0, value=10000.0)
newbalanceOrig = st.number_input("New Balance (Sender)", min_value=0.0, value=9000.0)
oldbalanceDest = st.number_input("Old Balance (Receiver)", min_value=0.0, value=0.0)
newbalanceDest = st.number_input("New Balance (Receiver)", min_value=0.0, value=0.0)


def _load_model(path: str):
    """Load the joblib model, raising an exception with traceback on failure."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model file not found: {path}")
    return joblib.load(path)


try:
    # Use Streamlit's resource cache if available to avoid reloading on every interaction
    try:
        cache_resource = st.cache_resource
    except Exception:
        # Older Streamlit versions may not have cache_resource; fall back to identity decorator
        def cache_resource(f):
            return f

    @cache_resource
    def get_model():
        return _load_model(MODEL_PATH)
except Exception:
    # This should not usually happen, but protect against failures reading Streamlit API
    get_model = None


if st.button("Predict"):
    input_data = pd.DataFrame({
        'type': [transaction_type],
        'amount': [amount],
        'oldbalanceOrg': [oldbalanceOrg],
        'newbalanceOrig': [newbalanceOrig],
        'oldbalanceDest': [oldbalanceDest],
        'newbalanceDest': [newbalanceDest]
    })

    # Load the model when prediction is requested. This avoids import-time failures
    # which can leave the Streamlit page blank.
    try:
        if get_model is None:
            raise RuntimeError("Model loader not available")

        with st.spinner('Loading model...'):
            model = get_model()
    except Exception:
        st.error("Failed to load model. See details below:")
        st.code(traceback.format_exc())
    else:
        try:
            prediction = model.predict(input_data)[0]
            st.subheader(f"Prediction Result : '{int(prediction)}'")

            if int(prediction) == 1:
                st.error("The transaction is predicted to be FRAUDULENT")
            else:
                st.success("The transaction looks like it is NOT A FRAUD")
        except Exception:
            st.error("Failed during prediction. See traceback:")
            st.code(traceback.format_exc())
