# -*- coding: utf-8 -*-
#
# This file is part of WEKO3.
# Copyright (C) 2017 National Institute of Informatics.
#
# WEKO3 is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# WEKO3 is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WEKO3; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.

# Use Python-3.5:
# FROM python:3.5
FROM python:3.5-slim
# FROM python:3.5-alpine


# Configure Weko instance:
ENV INVENIO_WEB_HOST=127.0.0.1
ENV INVENIO_WEB_INSTANCE=invenio
ENV INVENIO_WEB_VENV=invenio
ENV INVENIO_USER_EMAIL=info@inveniosoftware.org
ENV INVENIO_USER_PASS=uspass123
ENV INVENIO_POSTGRESQL_HOST=postgresql
ENV INVENIO_POSTGRESQL_DBNAME=invenio1
ENV INVENIO_POSTGRESQL_DBUSER=invenio1
ENV INVENIO_POSTGRESQL_DBPASS=dbpass123
ENV INVENIO_REDIS_HOST=redis
ENV REDIS_CACHE=0
ENV REDIS_SESSION=1
ENV REDIS_CELERY=2
ENV INVENIO_ELASTICSEARCH_HOST=elasticsearch
ENV INVENIO_RABBITMQ_HOST=rabbitmq
ENV INVENIO_WORKER_HOST=127.0.0.1
ENV SEARCH_INDEX_PREFIX=tenant1
 
# Install Weko web node pre-requisites:
RUN apt-get -y --no-install-recommends update --allow-releaseinfo-change && apt-get -y --no-install-recommends install curl git rlwrap screen vim gnupg
RUN curl -sL https://deb.nodesource.com/setup_4.x | bash -; printf "\nPackage: *\nPin: origin deb.nodesource.com\nPin-Priority: 600" >> /etc/apt/preferences.d/nodesource
RUN apt-get -y  --no-install-recommends install libffi-dev \
    libfreetype6-dev libjpeg-dev libmsgpack-dev libssl-dev build-essential\
    libtiff-dev libxml2-dev libxslt-dev nodejs python-dev \
    python-pip libpq-dev libreoffice fonts-ipafont \
    fonts-ipaexfont && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN su -c "npm install -g node-sass@3.8.0 clean-css@3.4.12 requirejs uglify-js" && pip --no-cache-dir install -U setuptools pip && pip --no-cache-dir install -U virtualenvwrapper 



# Add Weko sources to `code` and work there:
COPY packages-invenio.txt /code/packages-invenio.txt 
COPY packages.txt /code/packages.txt 
COPY requirements-weko-modules.txt /code/requirements-weko-modules.txt
COPY modules /code/modules
COPY scripts /code/scripts
COPY invenio /code/invenio
WORKDIR /code
#WORKDIR /code
#ADD . /code

# Run container as user `weko` with UID `1000`, which should match
# current host user in most situations:
RUN mkdir -p /usr/local/src && adduser --uid 1000 --disabled-password --gecos '' invenio && \
    chown -R invenio:invenio /code && chown -R invenio /usr/local/src
USER invenio

# Create Weko instance:
RUN /bin/bash -c  "source $(which virtualenvwrapper.sh);mkvirtualenv ${INVENIO_WEB_VENV};cdvirtualenv; \
    pip --no-cache-dir install -r /code/packages.txt; \
    pip --no-cache-dir install --no-deps -r /code/packages-invenio.txt; \
    pip --no-cache-dir install --no-deps -r /code/requirements-weko-modules.txt; \
    mkdir -p var/instance/; pip install jinja2-cli>=0.6.0;\
    jinja2 /code/scripts/instance.cfg > var/instance/${INVENIO_WEB_INSTANCE}.cfg; \
    ${INVENIO_WEB_INSTANCE} npm; \
    cdvirtualenv var/instance/static; \
    CI=true npm install angular-schema-form@0.8.13; \
    CI=true npm install;\
    cdvirtualenv var/instance/static/node_modules/ckeditor/plugins;\
    CI=true git clone https://github.com/nmmf/base64image.git; \
    ${INVENIO_WEB_INSTANCE} collect -v; \
    ${INVENIO_WEB_INSTANCE} assets build;\
    pip --no-cache-dir install gunicorn meinheld uwsgi uwsgitop; npm cache clean"


# Make given VENV default:
ENV PATH=/home/invenio/.virtualenvs/invenio/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV VIRTUALENVWRAPPER_PYTHON=/usr/local/bin/python
RUN echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc; echo "workon invenio" >> ~/.bashrc

# Start the Weko application:
CMD ["/bin/bash", "-c", "invenio run -h 0.0.0.0"]
# CMD ["/bin/bash", "-c", "gunicorn invenio_app.wsgi --workers=4 --worker-class=meinheld.gmeinheld.MeinheldWorker -b 0.0.0.0:5000 "]
#CMD ["/bin/bash","-c","uwsgi --ini /code/scripts/uwsgi.ini"]
