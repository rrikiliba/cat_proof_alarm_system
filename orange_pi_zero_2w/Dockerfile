FROM python:3.11.9-slim-bookworm
WORKDIR /alarm

COPY ./requirements.txt .

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install\
    gcc\ 
    python3-dev\
    libgl1\
    libgl1-mesa-glx \ 
    libglib2.0-0 -y && \
    rm -rf /var/lib/apt/lists/*


RUN pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu
RUN pip install -r requirements.txt

COPY ./*.py .
COPY ./model ./model
COPY ./static ./static

RUN useradd -m -r user
RUN chown user -R .
USER user

CMD [ "./app.py" ]
