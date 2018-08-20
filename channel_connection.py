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
        self.messages = []
        for i in range(5):
            m = bot.client.send_message(chan, "```BROWSER BOT PLACEHOLDER```")
            self.messages.append(m)


    async def update(self, servers):
        servers = sorted(servers, key=cmp_to_key(servers_sort))
        build = ["{:>20}\n====================\n".format("oapfs server browser")];
        msg_target = 0
        for s in servers:
            flag = ":question:"
            if "location" in s and "countryCode" in s["location"]:
                cc = s["location"]["countryCode"]
                if cc.upper() != "UN":
                    flag = ":flag_{}:".format(cc.lower())

            chunk_string = ""
            info = s["info"]
            chunk_string.append("{} **{}** ({})\n".format(flag, info["serverName"], info["gameDir"]))
            chunk_string.append("```====================\n")
            chunk_string.append("\tmap: {}\n".format(info["map"]))
            chunk_string.append("\tmode: {}\n".format(info["gameTypeShort"]))
            chunk_string.append("\tplayers: {}/{}\n".format(info["players"], info["maxPlayers"]))
            chunk_string.append("\tplay: /connect {}:{}\n".format(s["address"], s["port"]))
            chunk_string.append("====================```")
            if len(chunk_string) > 2000:
                print("Ignoring extra length server - {}".format(info["serverName"]))
                continue
            if len(build) + len(chunk_string) > 2000:
                await bot.client.edit_message(self.message[msg_target], new_content = build)
                build = chunk_string
            else:
                build.append(chunk_string)



