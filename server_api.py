import json
import time
import logging
import asyncio
import requests

class ServerAPI(object):
    def __init__(self, url, request_interval=60):
        self.url_base = url
        self.request_interval = request_interval
        self.bad_return = False

    async def get_updating_servers(self, path, interval = 30):
        """
        async generator for getting server data. runs every interval seconds.
        bad request to server url breaks the loop.
        there is no terminating condition here. use with async-for and break
        inside that to terminate!
        """
        url = self.url_base + path
        while True:
            await asyncio.sleep(interval)
            req = requests.get(url)
            if req.status_code != 200:
                logging.warn("BAD request @ " + url)
                # should this be an unchecked exception?
                self.bad_return = True
                break
            else:
                servers = json.loads(req.text)['servers']
                yield servers