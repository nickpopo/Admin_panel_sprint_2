FROM python:3.8

EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=config.settings.production
ENV DJANGO_STATIC_ROOT=/opt/app/static/
ENV DJANGO_MEDIA_ROOT=/opt/app/media/

RUN mkdir -p /usr/local/var/log/gunicorn/

WORKDIR /opt/app
RUN mkdir -p /opt/app/static/
RUN mkdir -p /opt/app/media/

COPY ./requirements/ ./requirements
RUN pip install -r requirements/production.txt

COPY . .

RUN python manage.py collectstatic --noinput -c

ENTRYPOINT [ "bash", "docker-entrypoint.sh" ]