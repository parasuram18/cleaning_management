FROM python:3.8.2-slim

RUN mkdir /project
WORKDIR /project

COPY requirements.txt /project

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
# COPY manage.py /project

COPY . /project
# ADD . /project

COPY start.sh /.
# RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/start.sh"]


CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]