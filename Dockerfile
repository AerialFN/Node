FROM python:3.8
WORKDIR /code
COPY . .
RUN pip install -U -r requirements.txt
CMD [ "python3", "main.py" ]
