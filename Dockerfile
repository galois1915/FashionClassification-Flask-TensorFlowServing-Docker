FROM python:3.10.13-alpine3.19
WORKDIR /app
COPY ./requirements.txt .
COPY ./main.py .
RUN pip install -r requirements.txt
ENV FLASK_APP=main.py
ENV FLASK_ENV=development
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=3000"]