FROM python:3.11 as poetry

COPY . /app

WORKDIR /app

RUN python3 -m pip install pipx && \
    python3 -m pipx ensurepath && \
    pipx install poetry==1.3.1 && \
    /root/.local/bin/poetry build --format wheel

FROM python:3.11 

COPY --from=poetry /app/dist/ /tmp/dist/

WORKDIR /app

RUN pip install /tmp/dist/*.whl

CMD trier-bot -f /config.ini