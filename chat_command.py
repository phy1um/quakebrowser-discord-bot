import warnings
import logging
import bot

chat_commands = {}
default_class = None


class ChatCommand(object):
    '''a command which is run in response to a chat command

    very non-OOP class for representing a chat command
    note: define a sub-class then call SubClass.register(..)
    instances are created through ChatCommand.process_text()
    do not manually create instances of this class or any inheriting
    classes!

    Attributes:
        args: array of arguments for the command executing
        chan: discord.py channel for the context this command executes in
        sender: discord.py user for the context ...
    '''
    # the prefix can be re-defined wherever, possibly per-chanhel-connection?
    command_prefix = "!"
    name = "PLACEHOLDER"

    def __init__(self):
        """setup new instance with placeholder values"""
        self.args = []
        self.chan = None
        self.sender = None

    def bind_args(self, tokens):
        """bind command arguments in an array

        note self.args[0] == registered name (like sys.argv)

        Args:
            tokens:
        """
        for t in tokens:
            self.args.append(t)

    def bind_context(self, channel, sender):
        """bind discord context for execution.

        note: this MUST be called before execute!

        Args:
            channel: discord.py channel object
            sender: ... user object
        """
        self.chan = channel
        self.sender = sender

    def _body(self):
        """override this for commands to implement execution functionality
        """
        warnings.warn("Default body in ChatCommand")
        return

    def execute(self):
        """perform the action associated with this command.

        do not override this in child classes. this is where logic for valid
        state is done because we cannot do that at instance construction!
        """
        if self.chan is None or self.sender is None:
            raise RuntimeError("Invalid ChatCommand state: no context bound")
        self._body()

    def _helptext(self):
        """
        override with explanatory text for a given command. used for generating
        help messages.
        """
        return "PLACEHOLDER"

    @classmethod
    def register(cls, name):
        """ register this CLASS with a given name, to be looked up in parsing

        Args:
            name: string name associating this class to a discord chat command
        """
        global chat_commands
        if name in chat_commands:
            # override for duplicate names, but log it!
            warnings.warn("Duplicate command registered - overriding "+name,
                          stacklevel=3)
        chat_commands[name] = cls
        cls.name = name

    @classmethod
    def process_text(cls, text):
        """parse text and check for a valid registered command call

        Args:
            text: string message from discord

        Returns:
            ChatCommand instance which can be executed, even if the command
                given in text was invalid (see set_default)
        """
        global chat_commands
        global default_class
        # early out for empty strings
        if len(text) < 0:
            return default_class()
        if text[0] == cls.command_prefix:
            # tokenize without prefix character
            tokens = text[1:].split(" ")
            # execute command name if known otherwise log
            if tokens[0] in chat_commands:
                cmd = chat_commands[tokens[0]]()
                cmd.bind_args(tokens)
                if cmd is None:
                    print("Somehow matched none command! {}".format(tokens[0]))
                return cmd
            else:
                logging.info("Unregistered command {} called".format(
                    tokens[0]))
                print("Returning default command handler class")
                return default_class()
        else:
            return default_class()

    @classmethod
    def set_default(cls):
        """set default class for process_text() commands where no command is found
        """
        print("Setting default chat command class globally")
        global default_class
        default_class = cls
        print(default_class)


class CommandNull(ChatCommand):
    """
    no-action "fallthrough" class for commands which do not map to classes
    """
    def _body(self):
        pass

# set this class as the default!
CommandNull.set_default()


class CommandsHelp(ChatCommand):
    """
    command for listing all commands
    """
    def _body(self):
        global chat_commands
        msg = "Commands list: \n```"
        for key in chat_commands:
            # do not print a message for ourself
            if key == self.__class__.name:
                continue
            # get helptext from temp instance of this class
            c = chat_commands[key]()
            msg += "{}: {}\n".format(key, c._helptext())
        # finally send message using bot.client (logged in client)
        bot.client.message_send(self.chan, msg)
