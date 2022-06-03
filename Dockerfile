FROM python:3.9
WORKDIR /FU
COPY src .
RUN pip3 install -r requirements.txt
EXPOSE 80
CMD ["python3", "main.py"]
