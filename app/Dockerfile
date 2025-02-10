FROM python:3.8-slim-buster

# UPDATE
RUN pip install --upgrade pip
RUN apt-get update -y
RUN apt-get upgrade -y


# DEPENDENCIES
WORKDIR /

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt


RUN mkdir ~/.streamlit
COPY config.toml config.toml
COPY credentials.toml credentials.toml
RUN cp config.toml ~/.streamlit/config.toml
RUN cp credentials.toml ~/.streamlit/credentials.toml

# START
COPY src /app
EXPOSE 8501
ENTRYPOINT ["streamlit", "run"]
CMD ["/app/main.py"]