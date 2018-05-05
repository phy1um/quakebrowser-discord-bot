import warnings
import logging
import bot

chat_commands = {}
default_class = lambda: None


class ChatCommand(object):
    ''' 
    very non-OOP class for representing a chat command
    note: define a sub-class then call SubClass.register(..)
    instances are created through ChatCommand.process_text()
    do not manually create instances of this class or any inheriting
    classes!'''
    # the prefix can be re-defined wherever, possibly per-chanhel-connection?
    command_prefix = "!"
    name = "PLACEHOLDER"

    def __init__(self):
        """
        setup new instance with placeholder values
        """
        self.args = []
        self.chan = None
        self.sender = None
        
    def bind_args(self, tokens):
        """
        bind command arguments in an array
        note self.args[0] == registered name (like sys.argv)
        """
        for t in tokens:
            self.args.append(t)

    def bind_context(self, channel, sender):
        """
        bind discord context, this MUST be called before execute!
        """
        self.chan = channel
        self.sender = sender

    def _body(self):
        """
        override this for commands to implement execution functionality
        """
        warnings.warn("Default body in ChatCommand")
        return

    def execute(self):
        """
        called to start execution - do not override this in child classes.
        this is where logic for valid state is done because we cannot do that
        at instance construction!
        """
        if self.chan == None or self.sender == None:
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
        """
        register this CLASS with a given name, to be looked up in parsing
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
        """
        parse text and check for a valid registered command call
        RETURNS: ChatCommand INSTANCE which can be executed
        """
        global chat_commands
        # early out for empty strings
        if len(text) < 0:
            return
        if text[0] == cls.command_prefix:
            # tokenize without prefix character
            tokens = text[1:].split(" ")
            # execute command name if known otherwise log
            if tokens[0] in chat_commands:
                cmd = chat_commands[tokens[0]]()
                cmd.bind_args(tokens)
                return cmd
            else:
                logging.info("Unregistered command {} called".format(tokens[0]))
                return default_class()

    @classmethod
    def set_default(cls):
        """
        set default class for process_text() commands where no command is found
        """
        global default_class
        default_class = cls
                

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
            