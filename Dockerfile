FROM ubuntu:18.04

EXPOSE 8009

WORKDIR /files/

# install third party dependencies of chromium browser but we don't need chromium itself
RUN apt-get update \
  && yes yes | apt-get install -y ttf-mscorefonts-installer \
  && apt-get install -y \
     build-essential python3-dev python3-pip python3-setuptools python3-wheel \
     fonts-font-awesome \
     libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip setuptools \
  && apt-get install -y chromium-browser \
  && apt-get remove -y chromium-browser \
  && rm -rf /var/lib/apt/lists/* && rm -rf /root/.cache/

ENTRYPOINT ["/usr/local/bin/gunicorn", "--bind=0.0.0.0:8009", \
              "wsgi:local_app", "--max-requests=300", \
              "--max-requests=500", "--max-requests-jitter=100", \
              "--workers=1", "--thread=1", "--timeout=30"]

COPY ./requirements.txt /files/requirements.txt

RUN pip3 install -r requirements.txt && rm -rf /root/.cache/

COPY ./ /files/

# trigger download of chrome
RUN python main.py
