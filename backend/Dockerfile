FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy existing modules required by backend
# We copy data and ml directories if they are needed by the backend
COPY data/ /app/data/
COPY ml/ /app/ml/
COPY backend/ /app/backend/

WORKDIR /app/backend

# Create a volume for the SQLite database
VOLUME /data
ENV DATABASE_URL="sqlite:////data/audit.db"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
