#!/usr/bin/env python3

from datetime import date, datetime

from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.types import ChannelParticipantsSearch

from IryoAirdrop.groupUsers import config


class TelegramGroupChecker():
    client = None

    def json_serial(obj):
        """JSON serializer for objects not serializable by default json code"""

        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError("Type %s not serializable" % type(obj))


    LIMIT = 100
    def connect(self):
        self.client = TelegramClient(config.phone, config.api_id, config.api_hash)
        self.client.connect()

        print ("Is user connected:" + "YES" if self.client.is_user_authorized() else " NO")

        if not self.client.is_user_authorized():
            self.client.send_code_request(config.phone)
            self.client.sign_in(code=int(input('Enter code: ')))

    #client.sign_in("""phone=config.phone""")
    #client.start(phone=config.phone)
    #me = client.sign_in(code=int(input('Enter code: ')))

    def isUserJoined(self, userID, channelName):
        try:
            LIMIT = 200
            channel = self.client(ResolveUsernameRequest(channelName)).chats[0]

            offset = 0
            output = []
            while True:
                participants = self.client(GetParticipantsRequest(
                    channel, ChannelParticipantsSearch(''), offset, LIMIT, hash=0))
                if not participants.users:
                    break

                offset += len(participants.users)

                for user in participants.users:
                    if userID == user.id:
                        return True
            return False
        except Exception as e:
            return 0