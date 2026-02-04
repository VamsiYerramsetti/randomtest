FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# We'll have Streamlit listen on 80 inside the container (simplifies Container Apps port)
ENV STREAMLIT_SERVER_PORT=80
EXPOSE 80

# avoid dev browser auto-open
ENV STREAMLIT_BROWSER_GATHERUSAGESTATS=false

CMD ["streamlit", "run", "app.py", "--server.port=80", "--server.address=0.0.0.0"]