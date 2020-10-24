FROM python:alpine

RUN set -ex \
  && addgroup bitcoin && adduser -D -G bitcoin bitcoin \
  && mkdir -p /home/bitcoin/app 

COPY . /home/bitcoin/app

RUN set -ex \
  && pip install -r /home/bitcoin/app/requirements.txt \
  && chown -Rf bitcoin:bitcoin /home/bitcoin/app


WORKDIR /home/bitcoin/app

USER bitcoin

CMD ["python", "app.py"]
  
