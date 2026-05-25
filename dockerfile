FROM python:latest

ENV PYTHONODONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip install --upgrade pip

RUN apt-get update && apt-get install -y default-libmysqlclient-dev build-essential

RUN pip install gunicorn

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir src

COPY . .

EXPOSE 8000
EXPOSE 3306 
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]