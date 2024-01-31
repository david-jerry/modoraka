release: python manage.py makemigrations && python manage.py migrate && python manage.py get_tokens
main: python main.py
web: gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker
worker: celery -A config.celery_app worker --loglevel=info
beat: celery -A config.celery_app beat --loglevel=info
