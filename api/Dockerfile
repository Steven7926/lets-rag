FROM python:3.10-slim

WORKDIR /api

COPY ./requirements.txt /api/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /api/requirements.txt \
    && pip uninstall -y setuptools

COPY ./app /api/app

ENV PYTHONPATH=/api

EXPOSE 8008

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8008", "--reload", "--reload-dir", "/api/app"]
