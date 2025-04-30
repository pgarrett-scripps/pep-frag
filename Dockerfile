FROM python:3.12-slim

WORKDIR /usr/src/app

# Set default values for environment variables
ENV PROJECT_TITLE="A Strealit App" \
    PROJECT_DESCRIPTION="A very descriptive description" \
    PROJECT_IMAGE_URL="https://example.com/image.jpg"

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["streamlit", "run", "app.py", "--server.port", "8501"]