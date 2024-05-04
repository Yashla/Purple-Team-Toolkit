FROM python:3.11
WORKDIR /myapp
COPY requirements.txt /myapp/
RUN pip install -r requirements.txt
COPY . /myapp
EXPOSE 5000
ENV NAME venv
CMD ["python3", "app.py"]