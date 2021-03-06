import bot
import pdb
from functools import cmp_to_key
from strings import SERVER_CHUNK_STRING


class ChannelCon(object):
    """connection between the server API and a discord channel.

        Every kind of action taken by this program on a discord channel can be
        represented by this abstraction. this class should be extended, and
        the sub-classes should override the (async) update() method. every
        instance of any subclass will be registered to the central "service"
        (and can be iterated over with other connections).

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


def servers_sort(a, b):
    return int(b["info"]["players"]) - int(a["info"]["players"])

async def get_send_message(c, m):
    return await bot.client.send_message(c, m)


class MessageSenderCon(ChannelCon):
    def __init__(self, chan, url_params, message_count=5):
        print("MAKING SENDER CONNECTION")
        super().__init__(chan, url_params)
        self.messages = []
        self.message_count = message_count

    async def make_messages(self):
        for i in range(self.message_count):
            m = await get_send_message(self.chan,
                                       "```BROWSER BOT PLACEHOLDER```")
            self.messages.append(m)

    async def update(self, servers):
        if len(self.messages) == 0:
            await self.make_messages()
        servers = sorted(servers, key=cmp_to_key(servers_sort))
        build = "{:>20}\n====================\n".format(
                "oapfs server browser")
        build = []
        build_len = 0
        build.append("{:>20}\n====================\n"
                     .format("oapfs server browser"))
        build_len += len(build[-1])

        msg_target = 0
        for s in servers:
            flag = ":question:"
            if "location" in s and "countryCode" in s["location"]:
                cc = s["location"]["countryCode"]
                if cc.upper() != "UN":
                    flag = ":flag_{}:".format(cc.lower())
            info = s["info"]
            chunk_string = SERVER_CHUNK_STRING.format(flag, info["serverName"],
                                                      info["gameDir"],
                                                      info["map"],
                                                      info["gameTypeShort"],
                                                      info["players"],
                                                      info["maxPlayers"],
                                                      s["address"],
                                                      s["port"])
            if len(chunk_string) > 2000:
                print("Ignoring extra length server - {}".format(
                    info["serverName"]))
                continue

            build.append(chunk_string)
            if build_len + len(chunk_string) > 2000:
                await bot.client.edit_message(self.messages[msg_target],
                                              "".join(build))
                msg_target += 1
                if msg_target >= len(self.messages):
                    print("Exceeded maximum post size for this bot")
                    return
                build = []
                build_len = 0
            else:
                build_len += len(build[-1])
        if len(build) > 0:
            await bot.client.edit_message(self.messages[msg_target],
                                          new_content="".join(build))
