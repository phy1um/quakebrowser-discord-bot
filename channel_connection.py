import bot
from functools import cmp_to_key

class ChannelCon(object):

    connections = []

    def __init__(self, chan, url_params):
        self.chan = chan
        self.url_params = url_params
        ChannelCon.register(self)

    def get_full_url(self, url_base):
        return "{}?{}".format(url_base, self.url_params)

    async def update(self, servers):
       pass 

    @classmethod
    def register(cls, obj):
        print("register {} as channel con".format(str(cls)))
        cls.connections.append(obj)

    @classmethod
    def remove(cls, chan):
        for c in cls.connections:
            if c.chan == chan:
                cls.connections.remove(c)
                return

    @classmethod
    async def connection_iter(cls):
        list_snapshot = cls.connections[:]
        for i in list_snapshot:
            yield i

def servers_sort(a,b):
    return int(b["info"]["players"]) - int(a["info"]["players"])

class MessageSenderCon(ChannelCon):
    def __init__(self, chan, url_params):
        print("MAKING SENDER CONNECTION")
        super().__init__(chan, url_params)
        self.last_msg = -1

    async def update(self, servers):
        servers = sorted(servers, key=cmp_to_key(servers_sort))
        build = "{:>20}\n====================\n".format("oapfs server browser");
        for s in servers:
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
        msg_hash = hash(build)
        if msg_hash == self.last_msg:
            return
        else:
            self.last_msg = msg_hash
            await bot.clear_chan(self.chan)
            await bot.client.send_message(self.chan, build)



            