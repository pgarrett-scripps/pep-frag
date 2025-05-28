FROM python:3.12-slim

# Create a non-root user to run the application
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create and properly configure the home directory for appuser
RUN mkdir -p /home/appuser && \
    chown -R appuser:appuser /home/appuser

WORKDIR /usr/src/app

# Install git and other dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        build-essential \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set proper permissions
RUN chown -R appuser:appuser /usr/src/app

# Set default values for environment variables
ENV PROJECT_TITLE="Pep-Frag" \
    PROJECT_DESCRIPTION="A Peptide Fragment Ion Calculator" \
    PROJECT_IMAGE_URL="https://github.com/pgarrett-scripps/pep-frag/blob/main/images/screenshot.png?raw=true" \
    GOOGLE_SITE_VERIFICATION_CODE="ZCyZCLoTV-n_EPpw68kWJmo19D8f2-NebLfnsZZXDKs"


ENV STREAMLIT_SERVER_PORT="8501" \
    STREAMLIT_SERVER_BASE_URL_PATH="" \
    STREAMLIT_ENABLE_COORS="true" \
    STREAMLIT_SERVER_ENABLE_CORS="true" \
    STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION="true" \
    STREAMLIT_SERVER_HEADLESS="true" \
    STREAMLIT_SERVER_MAX_UPLOAD_SIZE="200" \
    STREAMLIT_SERVER_ADDRESS="" \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS="false" \
    STREAMLIT_ENABLE_STATIC_SERVING="true" \
    STREAMLIT_FILE_WATCHER_TYPE="none" \
    STREAMLIT_CLIENT_TOOLBAR_MODE="viewer" \
    HOME="/home/appuser"

# Find streamlit's static directory and modify the index.html file
RUN STREAMLIT_PATH=$(python -c "import streamlit; import os; print(os.path.dirname(streamlit.__file__))") && \
    INDEX_PATH="$STREAMLIT_PATH/static/index.html" && \
    echo "Streamlit index.html found at: $INDEX_PATH" && \
    cp "$INDEX_PATH" "$INDEX_PATH.backup" && \
    sed -i "s|<head>|<head>\n    <!-- Google Site Verification -->\n    <meta name=\"google-site-verification\" content=\"$GOOGLE_SITE_VERIFICATION_CODE\" />\n\n    <!-- Primary Meta Tags -->\n    <meta\n      name=\"description\"\n      content=\"$PROJECT_DESCRIPTION\"\n    />\n\n    <!-- Open Graph / Facebook -->\n    <meta property=\"og:type\" content=\"website\" />\n    <meta property=\"og:url\" content=\"https://metatags.io/\" />\n    <meta property=\"og:title\" content=\"$PROJECT_TITLE\" />\n    <meta\n      property=\"og:description\"\n      content=\"$PROJECT_DESCRIPTION\"\n    />\n    <meta\n      property=\"og:image\"\n      content=\"$PROJECT_IMAGE_URL\"\n    />\n\n    <!-- Twitter -->\n    <meta property=\"twitter:card\" content=\"summary_large_image\" />\n    <meta property=\"twitter:url\" content=\"https://metatags.io/\" />\n    <meta property=\"twitter:title\" content=\"$PROJECT_TITLE\" />\n    <meta\n      property=\"twitter:description\"\n      content=\"$PROJECT_DESCRIPTION\"\n    />\n    <meta\n      property=\"twitter:image\"\n      content=\"$PROJECT_IMAGE_URL\"\n    />|" "$INDEX_PATH"

# Metadata labels
LABEL maintainer="Patrick Garrett <pgarrett@scripps.edu>"
LABEL version="1.0"
LABEL description="Streamlit Application for calculating a peptide's fragment ions"

# Add streamlit health check using environment variables
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl --fail "http://127.0.0.1:${STREAMLIT_SERVER_PORT}${STREAMLIT_SERVER_BASE_URL_PATH}/_stcore/health" || exit 1

# Expose the port that Streamlit runs on
EXPOSE 8501

# Switch to non-root user
USER appuser

# Start the Streamlit application
CMD ["streamlit", "run", "app.py"]
