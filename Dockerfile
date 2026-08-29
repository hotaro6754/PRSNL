FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for nfstream and others
RUN apt-get update && apt-get install -y \
    gcc \
    libcap-dev \
    libpcap-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    nfstream \
    fastapi \
    uvicorn \
    streamlit \
    pydantic \
    pandas \
    plotly \
    scikit-learn \
    requests

# The command will be overridden by docker-compose
CMD ["python", "-m", "http.server"]
