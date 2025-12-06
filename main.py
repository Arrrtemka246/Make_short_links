import argparse
import requests
import os
from urllib.parse import urlparse
from requests.exceptions import HTTPError
from dotenv import load_dotenv


class VKError(Exception):
    pass


def shorten_link(token, long_url):
    method_url = 'https://api.vk.ru/method/utils.getShortLink'
    
    params = {
        'access_token': token,
        'url': long_url,
        'v': '5.199'
    }
    
    response = requests.get(method_url, params=params)
    response.raise_for_status()
    
    api_response = response.json()
    
    if 'error' in api_response:
        error_message = api_response['error'].get('error_msg', 'Unknown error')
        raise VKError(f"VK API Error: {error_message}")
    
    return api_response['response']['short_url']


def count_clicks(token, short_url):
    method_url = 'https://api.vk.ru/method/utils.getLinkStats'
    
    url_key = short_url.split('/')[-1]
    
    params = {
        'access_token': token,
        'key': url_key,
        'interval': 'forever',
        'v': '5.199'
    }
    
    response = requests.get(method_url, params=params)
    response.raise_for_status()
    
    api_response = response.json()
    
    if 'error' in api_response:
        error_message = api_response['error'].get('error_msg', 'Unknown error')
        raise VKError(f"VK API Error: {error_message}")
    
    link_stats = api_response['response']['stats']
    return link_stats[0].get('views', 0) if link_stats else 0


def process_url(vk_token, user_url):
    if not user_url:
        print("Ошибка: Пустой ввод")
        return
    
    parsed_url = urlparse(user_url)
    if not all([parsed_url.scheme, parsed_url.netloc]):
        print("Ошибка: Неверный формат ссылки")
        return
    
    try:
        if parsed_url.netloc == 'vk.cc':
            click_count = count_clicks(vk_token, user_url)
            print(f"По вашей ссылке перешли {click_count} раз")
        else:
            short_url = shorten_link(vk_token, user_url)
            print(short_url)
            
    except HTTPError as error:
        print(f"Ошибка HTTP запроса: {error}")
    except VKError as error:
        print(f"Ошибка API VK: {error}")
    except Exception as error:
        print(f"Произошла непредвиденная ошибка: {error}")


def main():
    load_dotenv()
    vk_token = os.environ.get('VK_API_TOKEN')
    
    if not vk_token:
        print("Не найден VK API токен.")
        return
    
    parser = argparse.ArgumentParser(
        description='Сокращение ссылок и получение статистики через VK API'
    )
    parser.add_argument(
        'url',
        nargs='?',
        help='URL для обработки (сокращение или получение статистики)'
    )
    
    args = parser.parse_args()
    
    if args.url:
        process_url(vk_token, args.url.strip())
    else:
        user_url = input("Введите ссылку: ").strip()
        process_url(vk_token, user_url)


if __name__ == "__main__":
    main()