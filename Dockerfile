#GET UBUNTU 16.04
FROM ubuntu:16.04

#INSTALL DEPENDENCIES
RUN apt-get update -y && \
    apt-get install -y python-pip python-dev && \
    apt-get install -y postgresql-9.5 postgresql-contrib-9.5


#SETUP DATABASE
USER postgres
RUN /etc/init.d/postgresql start && \
    psql --command "CREATE USER pguser WITH SUPERUSER PASSWORD 'pguser';" && \
    createdb -O pguser james_finance && \
    createdb -O pguser james_finance_test

USER root

#SETUP ENV VARIABLES
ENV FLASK_APP="run.py"
ENV SECRET="B82593E5F64A31EB9C76488387C83"
ENV APP_SETTINGS="development"
ENV DATABASE_URL="postgresql://pguser:pguser@localhost/james_finance"
ENV TEST_DATABASE_URL="postgresql://pguser:pguser@localhost/james_finance_test"
ENV PGTZ="UTC"

#COPY FILES TO BUILD
COPY . /app

WORKDIR /app/api

#INSTALL PYTHON PACKAGES
RUN pip install -r requirements.txt

#EXECUTE SCRIPT AFTER BUILD
RUN chmod +x initialize.sh
CMD ./initialize.sh


