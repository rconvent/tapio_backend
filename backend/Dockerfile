# docker image
FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1

# Environment var
ENV HOME=/home/root \
    DEBIAN_FRONTEND=noninteractive \
    \
    ## PYTHON RELATED THINGS
    PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_NO_CACHE_DIR=on \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    #pyenv
    PYENV_ROOT=/home/root/.pyenv \
    \
    # poetry
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    \
    # this is where our requirements + virtual environment will live
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv" \
    VIRTUAL_ENV="/opt/pysetup/.venv"

# add poetry, pyenv etc to the path
ENV PATH=$POETRY_HOME/bin:$VENV_PATH/bin:${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PYENV_ROOT}/versions/${PYTHON_VERSION}/bin:$PATH


RUN apk update && apk upgrade
RUN apk add --no-cache --virtual .build-deps \
    ca-certificates \ 
    gcc \ 
    libpq-dev \
    postgresql-dev \ 
    python3-dev \
    linux-headers \
    musl-dev \
    libffi-dev \
    jpeg-dev \
    zlib-dev \
    automake \
    make \
    g++ \
    subversion

COPY ./pyproject.toml ${HOME}/app/pyproject.toml
COPY ./poetry.lock ${HOME}/app/poetry.lock

# install poetry and requirements
RUN pip3 install poetry

# Install dependencies globally (for ease of use)
RUN cd ${HOME}/app/ && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

# copy entrypoint.sh
COPY ./entrypoint.sh ${HOME}/app/entrypoint.sh
RUN sed -i 's/\r$//g' ${HOME}/app/entrypoint.sh
RUN chmod +x ${HOME}/app/entrypoint.sh

COPY . ${HOME}/app/
WORKDIR "${HOME}/app"

# run entrypoint.sh
# ENTRYPOINT ["/home/root/app/entrypoint.sh"]