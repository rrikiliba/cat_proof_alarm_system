FROM python:3.11.9-slim-bookworm
WORKDIR /alarm

COPY ./controller.py ./main.py
COPY ./static ./static

CMD [ "python3", "-u", "main.py" ]
