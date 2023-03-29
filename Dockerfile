FROM registry.access.redhat.com/ubi9/ubi:latest

RUN dnf install -y --nodocs --setopt=install_weak_deps=False \
        git \
        gcc \
        wget \
        python3.9 \
        python3.9-pip \
        python3.9-devel && \
        dnf clean all

WORKDIR /code
COPY ./server /code

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./data /data
ENV MOCK_DATA=/data

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config=logging.yaml"]
