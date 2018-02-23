import requests
import json
import asyncio
from functools import cmp_to_key

def playersCmp(a, b):
    #print("cmp {} > {}".format(a["info"]["players"], b["info"]["players"]))
    return int(b["info"]["players"]) - int(a["info"]["players"])

class ServerStatus:

    def __init__(self, url):
        self.url = url
        self._on_servers = asyncio.coroutine(lambda x: 0)
        self.servers = []
        self.last_msg = hash("")

    def update(self):
        req = requests.get(self.url)
        if req.status_code != 200:
            print("BAD request @ " + self.url)
            return
        else:
            servers = json.loads(req.text)['servers']
            self.servers = sorted(servers, key=cmp_to_key(playersCmp))
            self._do_on_servers(self.get_browser_string())


    def async_server_handler(self, fn):
        if not asyncio.iscoroutinefunction(fn):
            fn = asyncio.coroutine(fn)
        self._on_servers = fn
        return fn


    def _do_on_servers(self, m):
        loop = asyncio.get_event_loop()
        loop.create_task(self._on_servers(m))


    def get_browser_string(self):
        build = "{:>20}\n====================\n".format("oapfs server browser");

        for s in self.servers:
            flag = ":question:"
            if "location" in s and "countryCode" in s["location"]:
                cc = s["location"]["countryCode"]
                if cc.upper() != "UN":
                    flag = ":flag_{}:".format(cc.lower())

            info = s["info"]
            lines = "{} **{}** ({})\n".format(flag, info["serverName"], info["gameDir"])
            lines += "```====================\n"
            lines += "\tmap: {}\n".format(info["map"])
            lines += "\tmode: {}\n".format(info["gameTypeShort"])
            lines += "\tplayers: {}/{}\n".format(info["players"], info["maxPlayers"])
            lines += "\tplay: /connect {}:{}\n".format(s["address"], s["port"])
            lines += "====================```"

            build += lines
        return build


