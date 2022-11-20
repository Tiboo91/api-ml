FROM debian:latest

RUN apt-get update && apt-get install python3-pip -y && pip3 install pip install -r requirements.txt


ADD /source/server.py /fraudapi/main.py
ADD /source/knn_fraud_model.sav /fraudapi/knn_fraud_model.sav

WORKDIR /fraudapi/

EXPOSE 8000

CMD uvicorn main:app
