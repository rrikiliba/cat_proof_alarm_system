FROM python:3.11.9-slim-bookworm

ENV TINI_VERSION="v0.19.0"
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

WORKDIR /alarm

COPY ./requirements.txt .
RUN pip install -r requirements.txt

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install\
    libgl1\
    libgl1-mesa-glx \ 
    libglib2.0-0 -y && \
    rm -rf /var/lib/apt/lists/*

COPY ./.env .
COPY ./*.py .
COPY ./model ./model
COPY ./static ./static

RUN useradd -m -r user
RUN chown user -R .
USER user

ENTRYPOINT ["/tini", "--"]
CMD [ "./app.py" ]