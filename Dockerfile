FROM ubuntu:latest

WORKDIR /fraudapi

COPY ./main.py /fraudapi/main.py
COPY ./knn_fraud_model.sav /fraudapi/knn_fraud_model.sav
COPY ./requirements.txt  /fraudapi/requirements.txt

RUN apt-get update && apt-get install python3-pip -y && pip install -r requirements.txt 
RUN pip install uvicorn scikit-learn python-multipart

EXPOSE 8000

CMD ["uvicorn","main:app","--host", "0.0.0.0", "--port", "8000"]