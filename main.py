import requests
import os
from dotenv import load_dotenv
import argparse
import pandas as pd
from datetime import datetime
import json

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
PAYLOAD = {
    "video_auth_token": "A",
    "uuid": "A",
    "mobile": False,
    "device_info": {}
}
USERNAME = os.environ.get("FF_USER")
PASSWORD = os.environ.get("PASSWORD")
OBJECTS_PER_PAGE = 100
FINDFACE_ENDPOINT = "https://demo.ntechlab.com/"
DEFAULT_CARD_ID = "839"
COLUMNS_FOR_REPORT = ('episode', 'matched_card', 'person_name',
                      'created_date', 'thumbnail', 'fullframe', 'confidence',
                      'camera', 'camera_group')


def get_token_from_findface(url, user, password, payload):
    endpoint_url = f"{url}auth/login/"
    headers = {'content-type': 'application/json'}
    payload = json.dumps(payload)
    res = requests.post(endpoint_url, auth=(user, password),
                        data=payload, headers=headers)
    return res.json()['token']


def save_token_to_env_file(token):
    with open(".env", 'a') as f:
        f.write(f"\nTOKEN={token}")


def is_token_in_env():
    with open(".env") as f:
        return "TOKEN" in f.read()


def fetch_data_from_findface(endpoint_url, params):
    response = requests.get(endpoint_url, params=params)
    response.raise_for_status()
    return response.json()


def get_human_name_by_card_id(token, url, card_id):
    params = {'token': token}
    endpoint_url = f"{url}cards/humans/{card_id}"
    return fetch_data_from_findface(endpoint_url, params)["name"]


def fetch_data_by_card_id(token, url, card_id):
    params = {'token': token, "matched_card": card_id,
              'limit': OBJECTS_PER_PAGE}
    endpoint_url = f"{url}events/faces/"
    return fetch_data_from_findface(endpoint_url, params)


def fetch_data_by_event_id(token, url, event_id):
    params = {'token': token,
              "looks_like": f"faceevent:{event_id}",
              'limit': OBJECTS_PER_PAGE}
    endpoint_url = f"{url}events/faces/"
    return fetch_data_from_findface(endpoint_url, params)


def create_excel_report(data, person_name="N/A"):
    df = pd.json_normalize(data, record_path=["results"])
    df.insert(3, 'person_name', person_name)
    total_visits = data['count']
    last_visit = datetime.fromisoformat(data['results'][0]['created_date'])
    last_visit_formatted = last_visit.strftime("%d/%m/%Y, %H:%M:%S")
    total_visits_df = pd.DataFrame({"episode": [f"Всего визитов: {total_visits}", ]})
    last_time_visit_df = pd.DataFrame({"episode": [f"Последний визит: {last_visit_formatted}", ]})
    final_df = pd.concat([df, total_visits_df, last_time_visit_df], ignore_index=True)
    final_df.to_excel('report_from_script.xlsx', "report", columns=COLUMNS_FOR_REPORT)


if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser(description='Получение информации от FindFace API')
    cli_parser.add_argument('--card_id', nargs='?', help='Card_ID пользователя')
    cli_parser.add_argument('--event_id', nargs='?', help='ID события')
    card_id = cli_parser.parse_args().card_id
    event_id = cli_parser.parse_args().event_id
    # Если токена нет в .env файле, то запрашиваем новый и записываем его в файл
    if not is_token_in_env():
        save_token_to_env_file(get_token_from_findface(url=FINDFACE_ENDPOINT,
                                                       password=PASSWORD,
                                                       user=USERNAME,
                                                       payload=PAYLOAD))
    load_dotenv()
    TOKEN = os.environ.get("TOKEN")
    if card_id and not event_id:
        person_name = get_human_name_by_card_id(token=TOKEN,
                                                url=FINDFACE_ENDPOINT,
                                                card_id=card_id)
        data = fetch_data_by_card_id(token=TOKEN,
                                     url=FINDFACE_ENDPOINT,
                                     card_id=card_id)
        create_excel_report(data, person_name)
    elif event_id and not card_id:
        data = fetch_data_by_event_id(token=TOKEN,
                                      url=FINDFACE_ENDPOINT,
                                      event_id=event_id)
        create_excel_report(data)
    else:
        raise argparse.ArgumentError(message=f"Аргументы не указаны или указаны оба сразу")
