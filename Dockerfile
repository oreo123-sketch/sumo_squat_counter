FROM python:3.6.8-stretch as base

RUN pip install "poetry==1.0.5"
RUN apt update && \
  apt-get --no-install-recommends install -y gdebi-core
RUN wget -q -O wkhtmltox.stretch_amd64.deb https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.stretch_amd64.deb && \
  gdebi -n wkhtmltox.stretch_amd64.deb && \
  rm -f wkhtmltox.stretch_amd64.deb

FROM base as development

RUN curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
  apt-get --no-install-recommends install -y nodejs
RUN npm install -g pyright

WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi
COPY ./ ./

FROM base as production

WORKDIR /app
COPY poetry.lock pyproject.toml ./
# RUN poetry config virtualenvs.create false \
#   && poetry install --no-dev --no-interaction --no-ansi
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi
COPY ./ ./

# CMD poetry run python -m obschartpybackend
CMD python -m obschartpybackend
