import streamlit as st
from src.auth import require_auth
from src.config import config
from src.ml_engine import generate_signals
from src.visualization import plot_candlestick_with_signals, plot_probability_gauge
from src.database import db

st.set_page_config(page_title="Dashboard - AI Signals", layout="wide", page_icon="📈")
require_auth()

st.title(f"Welcome, {st.session_state.get('name', 'User')}")
st.markdown("### 10-Stock Signal Dashboard")

# Stock selector
selected_ticker = st.selectbox("Select Asset to Analyze", config.TARGET_TICKERS)

if st.button("Generate Latest Signal & Train Model", type="primary"):
    with st.spinner(f"Fetching data and running ML pipeline for {selected_ticker}..."):
        result = generate_signals(selected_ticker)
        
    if result:
        st.success(f"Signal Generated for {selected_ticker}!")
        
        # Save to DB if available
        if db.is_connected():
            db.save_predictions(selected_ticker, result['df_historical'].index[-1], result['signal'], {"accuracy": result['accuracy']})
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Latest Price", value=f"${result['latest_price']:.2f}")
        with col2:
            # Color coding the signal
            sig_color = "normal"
            if result['signal'] == "BUY": sig_color = "normal"
            elif result['signal'] == "SELL": sig_color = "inverse"
            else: sig_color = "off"
            
            st.metric(label="ML Prediction", value=result['signal'])
        with col3:
            st.metric(label="Model Evaluation Accuracy", value=f"{result['accuracy']:.2f}%", help="Based on backtested training accuracy for robustness against market noise (>85% targeted).")
            
        st.markdown("---")
        
        # Row for visualizations
        c1, c2 = st.columns([3, 1])
        with c1:
            fig_chart = plot_candlestick_with_signals(result['df_historical'], selected_ticker)
            st.plotly_chart(fig_chart, use_container_width=True)
            
        with c2:
            fig_gauge = plot_probability_gauge(result['confidence'], result['signal'])
            st.plotly_chart(fig_gauge, use_container_width=True)
            
    else:
        st.error(f"Error generating signal. Ensure data is accessible for {selected_ticker}.")
        
st.markdown("---")
if st.button("Logout"):
    st.session_state['logged_in'] = False
    st.rerun()
