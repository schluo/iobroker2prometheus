# IOBroker Object Data to Prometheus Exporter
Python based Prometheus Exporter

Can be used as Python Code or as Docker Container. 

Creation of Docker Container:

      docker build --tag iobroker2prometheus .

Starting of Docker Container with docker-compose

      docker-compose up -d

Credential, Ports and Polling Interval are given by environmental variables (see also the docker-compose.yml file)

    iobroker=password
    iobroker_host=<IP>
    exporter_port=9202
    loglevel=WARNING

