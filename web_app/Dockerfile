FROM python:3.7

COPY requirements.txt /src/
RUN pip install -r /src/requirements.txt

COPY /pack/ /src/pack/
COPY app_web/ /src/

CMD ["python", "/src/app.py"]