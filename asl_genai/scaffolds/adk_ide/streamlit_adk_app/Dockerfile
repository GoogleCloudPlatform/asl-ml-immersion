FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY assets /app/assets
COPY app.py /app

EXPOSE 8080

CMD streamlit run --server.port 8080 --server.enableCORS false app.py