FROM python:3.12-slim AS builder

WORKDIR /app/

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim

WORKDIR /app/

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

EXPOSE 8005

# Set the default command to run uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8005"]