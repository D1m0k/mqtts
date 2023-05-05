#!/usr/bin/python3
# -*- coding: utf-8 -*-
from paho.mqtt import client as mqtt_client
import json
import hashlib
import os
import re
import torch
import traceback
from dadata import Dadata
from normalizer import Normalizer
from pathlib import Path
from random import randint

token = os.environ.get("DADATA_TOKEN")
secret = os.environ.get("DADATA_SECRET")
dadata = Dadata(token, secret)

broker = os.environ.get("HOST", "localhost")
port = 1883
topic = "textToSpeech"
outtopic = "textToSpeechRes"
# generate client ID with pub prefix randomly
randint(100000, 999999)
client_id = f'CallBot{randint}'


# username = 'emqx'
# password = 'public'


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!", flush=True)
        else:
            print("Failed to connect, return code %d\n", flush=True)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        data = json.loads(msg.payload.decode())
        try:
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic", flush=True)
            text = data['text']
            if 'provider' in data:
                provider = data['provider']
            else:
                provider = 'default'
            hashtext = hashlib.md5(text.encode())
            hashfile = hashtext.hexdigest()
            prefix = '/sounds/'
            wavfile = f'{prefix}{hashfile}.wav'
            filename = f'{prefix}{hashfile}'
            print(wavfile, flush=True)
            rungen(text, wavfile, provider)
            data['ok'] = True
            data['status'] = "success"
            data['filename'] = hashfile
            jsout = json.dumps(data, ensure_ascii=False)
            client.publish(outtopic, jsout)
        except:
            data['error'] = traceback.format_exc()
            data['status'] = "error"
            jsout = json.dumps(data, ensure_ascii=False)
            print(jsout)
            client.publish(outtopic, jsout)

    client.subscribe(topic)
    client.on_message = on_message


def normalize(text_to_normalize, provider):
    if provider == 'top-delivery' or provider == 'default':
        if re.search(r'Стоимостью', text_to_normalize):
            pricestring = re.search(r'Стоимостью (\d+)', text_to_normalize)
            print('Recived price:', flush=True)
            print(text_to_normalize, flush=True)
            price = pricestring.groups([1])
            rub = int(price[0])
            rubs = 'рублей'
            if rub % 10 == 1:
                rubs = 'рубль'
    
            if 2 <= rub % 10 <= 4:
                rubs = 'рубля'
    
            text_to_normalize = re.sub(r'Стоимостью (\d+)', "Стоимостью {} {}".format(rub, rubs), text_to_normalize)
            print('Normalised price:', flush=True)
            print(text_to_normalize, flush=True)
    
        if re.search(r'(\d+\.\d+)\.\d+', text_to_normalize):
            datestring = re.findall(r'(\d+.\d+).\d+', text_to_normalize)
            print(f'Recived date in string: {text_to_normalize}')
            if len(datestring) > 1:
                date_begin = get_date(datestring[0])
                date_end = get_date_new(datestring[1])
                text_to_normalize = re.sub(r'с (\d+.\d+).\d+\sгода', f"с {date_begin}", text_to_normalize)
                text_to_normalize = re.sub(r'по (\d+.\d+).\d+\sгода', f"по {date_end}", text_to_normalize)
            else:
                date_begin = get_date(datestring[0])
                text_to_normalize = re.sub(r'(\d+.\d+).\d+\sгода', f" {date_begin}", text_to_normalize)
    
            print(f'Normalised date: {text_to_normalize}')
    
        if re.search(r'^Адрес доставки.*', text_to_normalize):
            print('Recived address:', flush=True)
            print(text_to_normalize, flush=True)
            result = dadata.clean("address", text_to_normalize)
            if result['city'] is None:
                address = f"Адрес доставки: {result['region_type_full']} {result['region']} {result['street_type_full']} {result['street']} {result['house_type_full']} {result['house']} {result['flat_type_full']} {result['flat']}"
            else:
                address = f"Адрес доставки: {result['city_type_full']} {result['city']} {result['street_type_full']} {result['street']} {result['house_type_full']} {result['house']} {result['flat_type_full']} {result['flat']}"
    
            address = address.replace('None', '')
            text_to_normalize = re.sub(r'\s\s+', ' ', address)
            text_to_normalize = re.sub(r'(\d+)\/(\d+)', r'\1 дробь \2', address)
            print('normalized address:', flush=True)
            print(text_to_normalize, flush=True)
    
        if re.search(r'.*\d.*', text_to_normalize):
            print('Recived text with digits:', flush=True)
            print(text_to_normalize, flush=True)
            torch.set_num_threads(os.cpu_count())
            norm = Normalizer()
            normtext = norm.norm_text(text_to_normalize)
            print('normalized text with digits:', flush=True)
            print(normtext, flush=True)
            return normtext
        else:
            print('Recived text:', flush=True)
            print(text_to_normalize, flush=True)
            normtext = text_to_normalize
            return normtext

    if provider == 'b2cpl':
        if re.search(r'Стоимостью', text_to_normalize):
            pricestring = re.search(r'Стоимостью (\d+)', text_to_normalize)
            print('Recived price:', flush=True)
            print(text_to_normalize, flush=True)
            price = pricestring.groups([1])
            rub = int(price[0])
            rubs = 'рублей'
            if rub % 10 == 1:
                rubs = 'рубль'

            if 2 <= rub % 10 <= 4:
                rubs = 'рубля'

            text_to_normalize = re.sub(r'Стоимостью (\d+)', "Стоимостью {} {}".format(rub, rubs), text_to_normalize)
            print('Normalised price:', flush=True)
            print(text_to_normalize, flush=True)

        if re.search(r'(\d+\.\d+)\.\d+', text_to_normalize):
            datestring = re.findall(r'(\d+.\d+).\d+', text_to_normalize)
            print(f'Recived date in string: {text_to_normalize}')
            if len(datestring) > 1:
                date_begin = get_date(datestring[0])
                date_end = get_date_new(datestring[1])
                text_to_normalize = re.sub(r'с (\d+.\d+).\d+\sгода', f"с {date_begin}", text_to_normalize)
                text_to_normalize = re.sub(r'по (\d+.\d+).\d+\sгода', f"по {date_end}", text_to_normalize)
            else:
                date_begin = get_date(datestring[0])
                text_to_normalize = re.sub(r'(\d+.\d+).\d+\sгода', f" {date_begin}", text_to_normalize)

            print(f'Normalised date: {text_to_normalize}')

        if re.search(r'^Адрес доставки.*', text_to_normalize):
            print('Recived address:', flush=True)
            print(text_to_normalize, flush=True)
            result = dadata.clean("address", text_to_normalize)
            if result['city'] is None:
                address = f"Адрес доставки: {result['region_type_full']} {result['region']} {result['street_type_full']} {result['street']} {result['house_type_full']} {result['house']} {result['flat_type_full']} {result['flat']}"
            else:
                address = f"Адрес доставки: {result['city_type_full']} {result['city']} {result['street_type_full']} {result['street']} {result['house_type_full']} {result['house']} {result['flat_type_full']} {result['flat']}"

            address = address.replace('None', '')
            text_to_normalize = re.sub(r'\s\s+', ' ', address)
            text_to_normalize = re.sub(r'(\d+)\/(\d+)', r'\1 дробь \2', address)
            print('normalized address:', flush=True)
            print(text_to_normalize, flush=True)

        if re.search(r'.*\d.*', text_to_normalize):
            print('Recived text with digits:', flush=True)
            print(text_to_normalize, flush=True)
            torch.set_num_threads(os.cpu_count())
            norm = Normalizer()
            normtext = norm.norm_text(text_to_normalize)
            print('normalized text with digits:', flush=True)
            print(normtext, flush=True)
            return normtext
        else:
            print('Recived text:', flush=True)
            print(text_to_normalize, flush=True)
            normtext = text_to_normalize
            return normtext
        

def gensound(text, save_path):
    path = Path(__file__).parent.absolute()
    modelpath = f'{path}/model.pt'
    device = torch.device('cpu')
    torch.set_num_threads(os.cpu_count())
    local_file = modelpath
    if not os.path.isfile(local_file):
        torch.hub.download_url_to_file('https://models.silero.ai/models/tts/ru/v3_1_ru.pt', local_file)

    model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
    model.to(device)
    sample_rate = 8000
    speaker = 'xenia'
    put_accent = True
    put_yo = True
    audio_paths = model.save_wav(text=text, speaker=speaker, sample_rate=sample_rate, put_accent=put_accent,
                                 put_yo=put_yo, audio_path=save_path)
    return save_path


def rungen(text, wavfile, provider):
    if not os.path.isfile(wavfile):
        text = normalize(text, provider)
        filename = gensound(text, wavfile)
        return filename

    return wavfile


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

def get_date(date):
    day_list = ['первого', 'второго', 'третьего', 'четвёртого',
                'пятого', 'шестого', 'седьмого', 'восьмого',
                'девятого', 'десятого', 'одиннадцатого', 'двенадцатого',
                'тринадцатого', 'четырнадцатого', 'пятнадцатого', 'шестнадцатого',
                'семнадцатого', 'восемнадцатого', 'девятнадцатого', 'двадцатого',
                'двадцать первого', 'двадцать второго', 'двадцать третьего',
                'двадацать четвёртого', 'двадцать пятого', 'двадцать шестого',
                'двадцать седьмого', 'двадцать восьмого', 'двадцать девятого',
                'тридцатого', 'тридцать первого']
    mounth_list = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                   'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    date_list = date.split('.')
    return day_list[int(date_list[0]) - 1] + ' ' + mounth_list[int(date_list[1]) - 1]


def get_date_new(date):
    day_list = ['первое', 'второе', 'третье', 'четвёртое',
                'пятое', 'шестое', 'седьмое', 'восьмое',
                'девятое', 'десятое', 'одиннадцатое', 'двенадцатое',
                'тринадцатое', 'четырнадцатое', 'пятнадцатое', 'шестнадцатое',
                'семнадцатое', 'восемнадцатое', 'девятнадцатое', 'двадцатое',
                'двадцать первое', 'двадцать второе', 'двадцать третье',
                'двадацать четвёртое', 'двадцать пятое', 'двадцать шестое',
                'двадцать седьмое', 'двадцать восьмое', 'двадцать девятое',
                'тридцатое', 'тридцать первое']
    mounth_list = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                   'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    date_list = date.split('.')
    return day_list[int(date_list[0]) - 1] + ' ' + mounth_list[int(date_list[1]) - 1]


if __name__ == '__main__':
    run()
