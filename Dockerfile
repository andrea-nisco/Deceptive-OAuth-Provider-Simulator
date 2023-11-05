FROM python:3.11.6-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
CMD ["python", "./app.py"]