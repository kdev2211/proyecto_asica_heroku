web: daphne -b 0.0.0.0 -p $PORT proyecto_asica_heroku.asgi:application
worker: celery -A proyecto_asica_heroku worker --loglevel=info
beat: celery -A proyecto_asica_heroku beat --loglevel=info