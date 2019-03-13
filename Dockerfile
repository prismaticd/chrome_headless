# note that pypy3 download is not ubuntu 18.04 compatible
FROM ubuntu:16.04

EXPOSE 8009

WORKDIR /files/

# install third party dependencies of chromium browser but we don't need chromium itself
RUN apt-get update \
  && apt-get install -y \
     wget bzip2 \
     build-essential \
     fonts-font-awesome \
     libexpat1 \
     libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info \
     libtiff5-dev libjpeg8-dev zlib1g-dev  libfreetype6-dev liblcms2-dev libwebp-dev libharfbuzz-dev \
     libfribidi-dev  tcl8.6-dev tk8.6-dev python-tk \
  && cd /opt/ && wget https://bitbucket.org/pypy/pypy/downloads/pypy3.5-v7.0.0-linux64.tar.bz2 \
  && tar xjf pypy3.5-v7.0.0-linux64.tar.bz2 && rm pypy3.5-v7.0.0-linux64.tar.bz2 \
  && rm -rf /var/lib/apt/lists/* && rm -rf /root/.cache/

ENTRYPOINT ["gunicorn", "--bind=0.0.0.0:8009", \
              "wsgi:local_app", "--max-requests=300", \
              "--max-requests=500", "--max-requests-jitter=100", \
              "--workers=1", "--thread=1", "--timeout=30"]

ENV PATH=/opt/pypy3.5-v7.0.0-linux64/bin/:${PATH}

RUN pypy3 -m ensurepip && pip3 install --upgrade pip wheel setuptools

COPY ./requirements.txt /files/requirements.txt

RUN pip install -r requirements.txt && rm -rf /root/.cache/

COPY ./ /files/
