#!/usr/bin/python3
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import sys
import collections
import datetime


SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SAMPLE_SPREADSHEET_ID = '' # fill in


def get_values():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range='A2:A1000').execute()
    specs = result.get('values', [])

    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range='B2:B1000').execute()
    rating = result.get('values', [])

    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range='C2:C1000').execute()
    hashes = result.get('values', [])

    if not specs or not rating:
        return None
    else:
        return list(zip(specs, rating, hashes))



specs = {
    'Теоретическая информатика': 'ti',
    'Распределённые системы': 'rs',
    'Машинное обучение и приложения': 'mop',
    'Анализ данных и интеллектуальные системы': 'adis',
    'Анализ и принятие решений': 'apr',
    'Математическая инженерия в науке и бизнесе': 'mi',
}



def get_one_list(values):
    global specs
    result = []
    for value in values:
        spec_name = None
        rating = None
        hash_value = None
        try:
            spec_name = specs[value[0][0]]
        except:
            pass
        try:
            rating = int(value[1][0]) - 1
        except:
            pass
        try:
            hash_value = value[2][0]
        except:
            pass
        result.append((spec_name, rating, hash_value))
    return result


BIN_COUNT = 6


def get_bin(x):
    if x is None:
        return (BIN_COUNT - 1)
    if x >= BIN_COUNT:
        return (BIN_COUNT - 1)
    return x



if __name__ == '__main__':
    values = get_values()
    if values is None:
        sys.exit()
    result = get_one_list(values)
    output = {spec_name: {index: 0 for index in range(BIN_COUNT)} for spec_name in specs.values()}

    info_dict = dict()

    for index, (spec, r_value, h_value) in enumerate(result):
        output[spec][get_bin(r_value)] += 1
        if h_value in info_dict:
            tmp = info_dict[h_value]
            output[tmp[0]][get_bin(tmp[1])] -= 1
        info_dict[h_value] = (spec, r_value, index)


    for spec in specs.values():
        output[spec]['total'] = sum([output[spec][x] for x in output[spec].keys()])

    with open('data.js', 'w') as f:
        f.write('var distrib = ' + str(output) + '\n')
    print('Success', datetime.datetime.now(), str(dict(output)))
