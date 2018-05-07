import bot
from functools import cmp_to_key

class ChannelCon(object):
    """connection between the server API and a discord channel.

        Every kind of action taken by this program on a discord channel can be
        represented by this abstraction. this class should be extended, and
        the sub-classes should override the (async) update() method. every
        instance of any subclass will be registered to the central "service"
        (and can be iterated over with other connections).

        Class Attributes:
            connections: array of registered connections (instances of this 
                class)

        Attributes:
            chan: a discord.py object representing the channel this connection 
                acts on
            url_params: the url parameters associated with the server info this 
                class will be acting on

    """
    connections = []

    def __init__(self, chan, url_params):
        """create and register connection for given channel"""
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
        build = ["{:>20}\n====================\n".format("oapfs server browser")];
        for s in servers:
            flag = ":question:"
            if "location" in s and "countryCode" in s["location"]:
                cc = s["location"]["countryCode"]
                if cc.upper() != "UN":
                    flag = ":flag_{}:".format(cc.lower())

            info = s["info"]
            build.append("{} **{}** ({})\n".format(flag, info["serverName"], info["gameDir"]))
            build.append("```====================\n")
            build.append("\tmap: {}\n".format(info["map"]))
            build.append("\tmode: {}\n".format(info["gameTypeShort"]))
            build.append("\tplayers: {}/{}\n".format(info["players"], info["maxPlayers"]))
            build.append("\tplay: /connect {}:{}\n".format(s["address"], s["port"]))
            build.append("====================```")

        message = build.join("")
        msg_hash = hash(message)
        if msg_hash == self.last_msg:
            return
        else:
            self.last_msg = msg_hash
            await bot.clear_chan(self.chan)
            await bot.client.send_message(self.chan, message)



            