# vim: ft=Dockerfile sw=4 ts=4 expandtab
ARG CI_BUILD_REF_NAME
ARG LOCALREG

FROM gladiatr72/just-tini:latest as tini

FROM revolutionsystems/python:3.7.2-wee-optimized-lto as builder-py

RUN pip install -U pip

COPY ./requirements.txt ./code/requirements.txt

RUN python3 -m venv /venv

RUN . /venv/bin/activate; pip install --no-compile  -r /code/requirements.txt

FROM revolutionsystems/python:3.7.2-wee-optimized-lto

ENV PYTHONWARNINGS ignore
ENV PYTHONDONTWRITEBYTECODE=true
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /code
ENV PATH /venv/bin:/bin:/usr/bin:/usr/local/bin

RUN mkdir /code
COPY --from=tini /tini /

COPY . /code/
COPY --from=builder-py /venv/ /venv/
COPY --from=builder-py /code/ /code/

WORKDIR /code

ENTRYPOINT ["/tini", "--"]

CMD ["gunicorn", "-c", "/code/gunicorn.conf", "config.wsgi"]

ENV X_IMAGE_TAG v0.0.0

LABEL Description="{{ cookiecutter.project_name}} Image" Vendor="REVSYS"
LABEL Version="${X_IMAGE_TAG}"

