# /backend/dockerfile
# Using Debian bullseye-slim as base image
FROM python:3.11-slim-bullseye

# Set the working directory to /app
WORKDIR /app/backend
COPY ./backend/requirements.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends --allow-change-held-packages \
        wget \
        curl \
        python3-full \
        python3-pip \
        python3-dev \
        gcc \
        make \
        git && \
    apt-get clean autoclean && \
    apt-get autoremove --yes && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    pip install --no-cache-dir --upgrade pip setuptools

RUN apt-get purge -y --auto-remove ca-certificates

# Work around for `[nltk_data]     CERTIFICATE_VERIFY_FAILED] certificate verify failed:` error
# ToDo: Work around still doesnt work
# https://stackoverflow.com/questions/41348621/ssl-error-downloading-nltk-data
RUN pip install --upgrade certifi

# Install software needed for handling various file processing
RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-java-common \
    ffmpeg && \
    apt-get clean autoclean && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/apt/lists/*

# Install the requirements
RUN pip install --trusted-host pypi.org -r requirements.txt

# Install NLTK and download the punkt and averaged_perceptron_tagger data
ENV NLTK_PATH="src/ingestor/nltk_data"
RUN python3 -m pip install nltk && \
    python3 -c "import nltk; nltk.download('punkt', download_dir='src/ingestor/nltk_data/punkt')" && \
    python3 -c "import nltk; nltk.download('averaged_perceptron_tagger', download_dir='app/ingestor/nltk_data/averaged_perceptron_tagger')"

# Copy the current directory contents into the container at /app
COPY . .

ENV PYTHONPATH "${PYTHONPATH}:/app/backend"

# Start a bash shell and source the CHATBOT_NAME value from /etc/bash.bashrc
# Include templates/ dir so that agent changes also reload the program
CMD ["uvicorn", "src.main:app", "--log-level", "debug", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# NOTE for WSL: When using Uvicorn through WSL, you might have to set the WATCHFILES_FORCE_POLLING environment variable, for file changes to trigger a reload. See watchfiles documentation for further details.
