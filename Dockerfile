FROM debian:latest


ADD ./source/server.py /fraudapi/main.py
ADD ./source/knn_fraud_model.sav /fraudapi/knn_fraud_model.sav
ADD requirements.txt  /fraudapi/requirements.txt
RUN apt-get update && apt-get install python3-pip -y && pip install -r requirements.txt
WORKDIR /fraudapi/

EXPOSE 8000

CMD uvicorn main:app
