FROM debian:latest


ADD ./source/main.py /fraudapi/main.py
ADD ./source/knn_fraud_model.sav /fraudapi/knn_fraud_model.sav
ADD requirements.txt  /fraudapi/requirements.txt

WORKDIR /fraudapi/
RUN apt-get update && apt-get install python3-pip -y && pip install -r requirements.txt
EXPOSE 8000

CMD uvicorn main:app
