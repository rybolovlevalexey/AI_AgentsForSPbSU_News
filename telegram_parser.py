from telethon.sync import TelegramClient
from telethon import connection
import asyncio
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.functions.messages import GetHistoryRequest
import json
from datetime import date, datetime


api_id = 25747007
api_hash = "c12140719698e4ec454f50ae9c1eda06"
username = "rybolovlevalexey"

client = TelegramClient(username, api_id, api_hash)
client.start()

channel = client.get_entity("https://t.me/spbuniversity1724")

async def dump_all_messages(channel):
    offset_msg = 0    # номер записи, с которой начинается считывание
	limit_msg: int = 100   # максимальное число записей, передаваемых за один раз

	all_messages = []   # список всех сообщений
	total_messages = 0
	total_count_limit = 0  # поменяйте это значение, если вам нужны не все сообщения

	class DateTimeEncoder(json.JSONEncoder):
		'''Класс для сериализации записи дат в JSON'''
		def default(self, o):
			if isinstance(o, datetime):
				return o.isoformat()
			if isinstance(o, bytes):
				return list(o)
			return json.JSONEncoder.default(self, o)

	while True:
		history = await client(GetHistoryRequest(
			peer=channel,
			offset_id=offset_msg,
			offset_date=None, add_offset=0,
			limit=limit_msg, max_id=0, min_id=0,
			hash=0))
		if not history.messages:
			break
		messages = history.messages
		for message in messages:
			all_messages.append(message.to_dict())
		offset_msg = messages[len(messages) - 1].id
		total_messages = len(all_messages)
		if total_count_limit != 0 and total_messages >= total_count_limit:
			break

	with open('channel_messages.json', 'w', encoding='utf8') as outfile:
		 json.dump(all_messages, outfile, ensure_ascii=False, cls=DateTimeEncoder)


async def main():
	url = input("Введите ссылку на канал или чат: ")
	channel = await client.get_entity(url)
	await dump_all_messages(channel)
