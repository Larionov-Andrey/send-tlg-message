import asyncio
import os

import path

from config import api_id, api_hash
from telethon.sync import TelegramClient, events


class TG():
    # client: TelegramClient

    def create_session(self):

        client = TelegramClient('anon', api_id, api_hash)
        client.start()
        client.disconnect()

    def send_message(self, text, to, media=None):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print(text)
        client = TelegramClient('anon', api_id, api_hash)
        client.start()
        try:
            if 'http' in to:
                channel =  client.get_entity(to)
            else:
                channel = to
            out_media = None if not media or len(media) == 0 else [i for i in media]


            if out_media != None:
                for i in range(len(out_media)):

                    out_media[i] = path.Path('./static' + out_media[i]).abspath()


            client.send_message(entity=channel, message=text, parse_mode='md', file=out_media)

            client.disconnect()
            loop.close()

            return True
        except Exception as e:
            print(e)
            client.disconnect()
            loop.close()

            return False


def test():
    print(123)
    tg = TG()
    tg.send_message('tex', 'rss_bot')

if __name__ == '__main__':
    from apscheduler.schedulers.background import BackgroundScheduler
    s = BackgroundScheduler()
    s.add_job(test, 'interval', seconds=5)
    s.start()
    asyncio.get_event_loop().run_forever()
