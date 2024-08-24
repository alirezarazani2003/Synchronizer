FROM python:3.10.5-slim
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY . /app

## program run methods
CMD ["uvicorn", "main:app", "--host" , "0.0.0.0" , "--port" , "5223" , "--reload"]
