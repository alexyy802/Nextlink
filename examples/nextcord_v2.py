from nextcord.ext import commands
import nextlink
import nextcord
import zlib


class Music(commands.Cog, nextlink.NextlinkMixin):
    def __init__(self, bot):
        self.bot = bot
        self.nextlink = nextlink.Client(bot=bot)
        bot._enable_debug_events = True
        self._zlib = zlib.decompressobj()
        self._buffer = bytearray()
        bot.add_listener(self.nextlink.update_handler, 'on_socket_custom_receive')
        self.bot.loop.create_task(self.start_nodes())

    @commands.Cog.listener()
    async def on_socket_raw_receive(self, msg):
        """ This is to replicate discord.py's 'on_socket_response' that was removed from discord.py v2 """
        if type(msg) is bytes:
            self._buffer.extend(msg)

            if len(msg) < 4 or msg[-4:] != b'\x00\x00\xff\xff':
                return

            try:
                msg = self._zlib.decompress(self._buffer)
            except Exception:
                self._buffer = bytearray()  # Reset buffer on fail just in case...
                return

            msg = msg.decode('utf-8')
            self._buffer = bytearray()

        msg = nextcord.utils._from_json(msg)
        self.bot.dispatch("socket_custom_receive", msg)    