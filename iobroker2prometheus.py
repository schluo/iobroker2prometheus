#!/usr/bin/env python3
# encoding: utf-8

__author__ = "Oliver Schlueter"
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "oliver.schlueter@dell.com"
__status__ = "Production"

""""
###########################################################################################################
  Prometheus Exporter for Mitsubishi MelCloud Devices

 Permission is hereby granted, free of charge, to any person obtaining a copy of this software 
  and associated documentation files (the "Software"), to deal in the Software without restriction, 
  including without limitation the rights to use, copy, modify, merge, publish, distribute, 
  sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is 
  furnished to do so, subject to the following conditions:
  The above copyright notice and this permission notice shall be included in all copies or substantial 
  portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT 
  LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
###########################################################################################################
"""

import datetime
import json
import os
import time
import requests

from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY

class IOBroker2Prometheus(object):

    def __init__(self, iobroker_host, iobroker_user, iobroker_password, IOBrokerDataPoints):
        self.iobroker_host = iobroker_host
        self.iobroker_password = iobroker_password
        self.iobroker_user = iobroker_user
        self.GaugeMetricFamilies = []
        self.Infos = []
        self.IOBrokerDataPoints = IOBrokerDataPoints

        self.data = {
            "User": self.iobroker_user,
            "Password": self.iobroker_password,
            "AppVersion": "1.23.4.0"
        }

    def create_gauge_metric_families(self):
        self.GaugeMetricFamilies.clear()
        self.Infos.clear()
        for DataPoint in self.IOBrokerDataPoints:
            io_broker_object_name = DataPoint.split(".")[0].replace("-", "_")
            dp_exists = False

            for i in self.GaugeMetricFamilies:
                if io_broker_object_name == i.name:
                    dp_exists = True
            if not dp_exists:
                self.GaugeMetricFamilies.append(
                    GaugeMetricFamily(io_broker_object_name, io_broker_object_name, labels=['sensor']))

    def collect(self):
        timestamp = datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")

        self.create_gauge_metric_families()

        return_type = None
        for DataPoint in self.IOBrokerDataPoints:
            try:
                # try to get device data
                url = f'http://{self.iobroker_host}:8087/get/{DataPoint}'
                url = url.strip()
                # response = requests.get(url, headers=self.headers, data=json.dumps(self.data))
                response = requests.get(url)
                out = json.loads(response.text)
                value = out['val']
                return_type = out['common']['type']
            except Exception as err:
                print(timestamp + ": Not able to get device data: " + str(err))
                value = -1

            if return_type == 'number':
                for gauge_metric_family in self.GaugeMetricFamilies:
                    FamilyName = DataPoint.split('.')[0]
                    MetricName = DataPoint.replace(FamilyName + '.0.', "")

                    FamilyName = FamilyName.replace('-', '_')
                    if gauge_metric_family.name == FamilyName:
                        gauge_metric_family.add_metric([MetricName], value)

        for gauge_metric_family in self.GaugeMetricFamilies:
            yield gauge_metric_family


def main():
    """Main entry point"""

    try:
        filename = os.environ['IOBROKER_DP_FILE']
        print(filename)
    except:
        print('No Datapoint file found')
        exit(1)

    try:
        file1 = open(filename, 'r')
        IOBrokerDataPoints = file1.readlines()
    except Exception as err:
        print('No Datapoint file load: '+ err)
        exit(1)

    try:
        port = int(os.environ['EXPORTER_PORT'])
    except:
        port = 8022

    try:
        iobroker_host = os.environ['IOBROKER_HOST']
    except:
        iobroker_host = "127.0.0.1"

    try:
        iobroker_user = os.environ['IOBROKER_USER']
    except:
        iobroker_user = "user"

    try:
        iobroker_password = os.environ['IOBROKER_PASSWORD']
    except:
        iobroker_password = "password!"

    start_http_server(port)

    REGISTRY.register(IOBroker2Prometheus(iobroker_host, iobroker_user, iobroker_password, IOBrokerDataPoints))

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
