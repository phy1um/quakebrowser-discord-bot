import json
import time
import logging
import asyncio
import requests


class ServerAPI(object):
    """abscraction for getting data from a quake server API

    abstracts requests for any API compliant with DOCUMENTATION LINK.
    all work is done by the generator async get_updating_servers() call.
    """
    def __init__(self, url):
        """create new server API link

        Args:
            url: string of the API base url (no params)
        """
        self.url_base = url
        self.bad_return = False

    async def get_updating_servers(self, path, interval=30):
        """async generator for getting server data.

        runs every interval seconds. bad request to server url breaks the loop.
        there is no terminating condition here. use with async-for and break
        inside that to terminate!

        Args:
            path: string parameter to be appended to the url_base for requests
            interval: number of seconds to wait between api requests

        Yields:
            array of server JSON data (according to DOCUMENTATION LINK)
        """
        url = "{}?{}".format(self.url_base, path)
        while True:
            # stop for our interval
            await asyncio.sleep(interval)
            # get data from API
            req = requests.get(url)
            if req.status_code != 200:
                logging.warn("BAD request @ " + url)
                # should this be an unchecked exception?
                self.bad_return = True
                break
            else:
                # convert to JSON and yield
                servers = json.loads(req.text)['servers']
                yield servers
