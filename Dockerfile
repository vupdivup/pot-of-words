FROM python:3.13

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src src

RUN [ "python", "src/etl.py" ]

EXPOSE 5000

CMD [ "flask", "--app", "src/app.py", "run", "--host", "0.0.0.0" ]