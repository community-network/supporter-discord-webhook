FROM python:3.9

WORKDIR /usr/src/app

COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./webhooks.py webhooks.py

CMD python ./webhooks.py
