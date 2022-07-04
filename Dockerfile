FROM python:3.9
WORKDIR /FU
COPY src /FU/src/
COPY  assets /FU/assets/
RUN pip3 install -r requirements.txt
EXPOSE 80
CMD ["python3", "/FU/src/main.py"]
