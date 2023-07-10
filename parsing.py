import requests
import time
import csv
import re

token = "905d62ba905d62ba905d62ba93934edea29905d905d62baf41bd2b212a7ee2ff563da6f" # Токен
version = 5.131 # Версия API

# Для получения комментариев нужен owner_id группы, получаем его
def get_owner_id(domain):
    response = requests.get("https://api.vk.com/method/groups.getById",
                            params={
                                "access_token": token,
                                "v": version,
                                "group_id": domain
                            }
                            )

    group_info = response.json()['response']
    id = group_info[0]['id']
    owner_id = -id

    return owner_id

# Комментарий можно получить только зная id поста, получаем id постов
def get_posts_id_list(domain, count):
    response = requests.get("https://api.vk.com/method/wall.get",
                            params={
                                "access_token": token,
                                "v": version,
                                "domain": domain,
                                "count": count
                            }
                            )

    data = response.json()['response']['items']

    posts_id = []
    for item in data:
        if item['comments']['count'] != 0:
            posts_id.append(item['id'])
    
    return posts_id

# Получаем список комментариев
def get_comments_list(owner_id, posts_id_list):
    comments = []
    sleep_counter = 5
    counter = 0

    for i in posts_id_list:
        if(counter == sleep_counter): # у VK API установлено ограничение на кол-во запросов, делаем задержку 
            time.sleep(1)
            counter = 0
        
        response = requests.get("https://api.vk.com/method/wall.getComments",
                                params={
                                    "access_token": token,
                                    "v": version,
                                    "owner_id": owner_id,
                                    "post_id": i 
                                }
                                )
        debug = response.json()
        post_comments = response.json()['response']['items']
    
        for item in post_comments:
            if(len(item['text']) != 0): 
                comments.append(item['text'])
        counter += 1
    
    return comments

# Записываем комменты в csv
def write_csv(name, comments_list):
    with open(name, 'w', encoding='utf-8') as file:
        pen = csv.writer(file)
        pen.writerow((['comment']))
        for comment in comments_list:
            pen.writerow(([comment]))

# Удаляем escape-последовательности из комментов
def clear_escapes(comments_list):
    new_comments = []
    for comment in comments_list:
        comment = re.sub(r'\n', ' ', comment)
        new_comments.append(comment)
    return new_comments

def main(domain):
    owner_id = get_owner_id(domain)
    posts_id = get_posts_id_list(domain, 100) # Парсятся 100 последних постов
    all_comments = get_comments_list(owner_id, posts_id)
    all_comments = clear_escapes(all_comments)
    write_csv(r'pars_comments/' + domain + '.csv', all_comments)

    return len(all_comments)



