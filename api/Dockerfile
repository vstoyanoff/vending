FROM python:3.9.7-buster
# The SHELL statement below makes RUN commands a bit more robust and easier to debug.
# More details: https://bit.ly/2InCT2P (link to bash documentation).
SHELL ["/bin/bash", "-o", "pipefail", "-o", "errexit", "-o", "nounset", "-o", "xtrace", "-c"]

ENV PATH=/home/vending/venv/bin:/opt/poetry/bin:${PATH} \
    VIRTUAL_ENV=/home/vending/venv

RUN python -m venv /opt/poetry ; \
    /opt/poetry/bin/pip install --upgrade --progress-bar=off pip setuptools wheel ; \
    /opt/poetry/bin/pip install --progress-bar=off "poetry>=1.1.0,<1.2.0"

COPY pyproject.toml poetry.lock /home/vending/code/

WORKDIR /home/vending/code

RUN python -m venv $VIRTUAL_ENV ; \
    pip install --upgrade --progress-bar=off pip setuptools wheel ; \
    poetry install --no-dev --no-interaction ; \
    rm -rf /home/vending/.cache/pip

COPY . /home/vending/code

# doing poetry install the second time to install the project
RUN poetry install --no-dev --no-interaction ;
