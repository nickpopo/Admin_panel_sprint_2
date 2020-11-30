FROM python:3.8

VOLUME /opt/media


EXPOSE 8000

RUN mkdir -p /usr/local/var/log/gunicorn/

WORKDIR /opt/app
RUN mkdir -p /opt/app/static/
RUN mkdir -p /opt/app/media/

COPY ./requirements/ ./requirements
RUN pip install -r requirements/production.txt


COPY . .


RUN python manage.py collectstatic --noinput -c


CMD ["gunicorn", "-c", "gunicorn.conf.py", "config.wsgi"]