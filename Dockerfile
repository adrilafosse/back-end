FROM python:3.10-slim

RUN pip install --upgrade pip

# Copy the application files
COPY . /app
WORKDIR /app

# Install dependencies
RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["python", "back-end.py"]

