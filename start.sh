#!/bin/bash
set -e

echo "Starting Stock Portfolio Dashboard..."
echo "Python version: $(python --version)"
echo "Streamlit version: $(python -c 'import streamlit; print(streamlit.__version__)')"
echo "Current directory: $(pwd)"
echo "PORT: ${PORT:-8080}"

# Run Streamlit
streamlit run app.py \
  --server.port=${PORT:-8080} \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --logger.level=debug
