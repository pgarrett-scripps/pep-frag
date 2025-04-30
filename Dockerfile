FROM python:3.12-slim

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

# Set default values for environment variables
ENV PROJECT_TITLE="Pep-Frag" \
    PROJECT_DESCRIPTION="A Peptide Fragment Ion Calculator" \
    PROJECT_IMAGE_URL="https://example.com/image.jpg"

# Find streamlit's static directory and modify the index.html file
RUN STREAMLIT_PATH=$(python -c "import streamlit; import os; print(os.path.dirname(streamlit.__file__))") && \
    INDEX_PATH="$STREAMLIT_PATH/static/index.html" && \
    echo "Streamlit index.html found at: $INDEX_PATH" && \
    cp "$INDEX_PATH" "$INDEX_PATH.backup" && \
    sed -i "s|<head>|<head>\n    <!-- Primary Meta Tags -->\n    <meta\n      name=\"description\"\n      content=\"$PROJECT_DESCRIPTION\"\n    />\n\n    <!-- Open Graph / Facebook -->\n    <meta property=\"og:type\" content=\"website\" />\n    <meta property=\"og:url\" content=\"https://metatags.io/\" />\n    <meta property=\"og:title\" content=\"$PROJECT_TITLE\" />\n    <meta\n      property=\"og:description\"\n      content=\"$PROJECT_DESCRIPTION\"\n    />\n    <meta\n      property=\"og:image\"\n      content=\"$PROJECT_IMAGE_URL\"\n    />\n\n    <!-- Twitter -->\n    <meta property=\"twitter:card\" content=\"summary_large_image\" />\n    <meta property=\"twitter:url\" content=\"https://metatags.io/\" />\n    <meta property=\"twitter:title\" content=\"$PROJECT_TITLE\" />\n    <meta\n      property=\"twitter:description\"\n      content=\"$PROJECT_DESCRIPTION\"\n    />\n    <meta\n      property=\"twitter:image\"\n      content=\"$PROJECT_IMAGE_URL\"\n    />|" "$INDEX_PATH"

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port", "8501"]