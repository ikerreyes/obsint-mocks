FROM registry.access.redhat.com/ubi9/ubi-minimal:latest

RUN microdnf install --nodocs --noplugins -y python3.11 python3.11-pip

WORKDIR /code
COPY ./server /code

RUN python3.11 -m pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./data /data
ENV MOCK_DATA=/data

RUN microdnf clean all
RUN rpm -e --nodeps sqlite-libs krb5-libs libxml2 readline

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config=logging.yaml"]
