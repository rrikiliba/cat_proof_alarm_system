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
RUN pip3 install -r requirements.txt

COPY ./controller.py ./main.py
COPY ./model ./model

CMD [ "python3", "-u", "main.py" ]
