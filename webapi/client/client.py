import requests
import json

BASE_URL = "https://newssites.pythonanywhere.com/api/"


class Client:
    def __init__(self):
        self.session = requests.Session()  # 创建一个会话对象
        self.logged_in = False
        self.news_service_url = None

    def login(self, url):
        self.news_service_url = url
        username = input("Enter username: ")
        password = input("Enter password: ")
        payload = {
            "username": username,
            "password": password
        }
        try:
            response = self.session.post(self.news_service_url + "api/login", data=payload)
            response.raise_for_status()  # 检查响应是否为 200
            self.logged_in = True
            print("Logged in successfully.")
            print("Session cookies:", self.session.cookies)
        except requests.RequestException as e:
            print("Failed to log in:", str(e))

    def logout(self):
        if self.logged_in:
            self.logged_in = False
            self.session.close()  # 关闭会话对象
            print("Logged out successfully.")

    def post_story(self):
        if not self.logged_in:
            print("Please login first.")
            return

        headline = input("Enter headline: ")
        category = input("Enter category: ")
        region = input("Enter region: ")
        details = input("Enter details: ")

        payload = {
            "headline": headline,
            "category": category,
            "region": region,
            "details": details
        }

        try:
            # 发布故事前首先检查登录状态，确保用户已登录
            # if not self.session.cookies.get('sessionid'):
            #     print("Please login first.")
            #     return
            print(self.news_service_url + "api/stories")
            print(payload)
            response = self.session.post(self.news_service_url + "api/stories", json=payload)
            response.raise_for_status()  # 检查响应是否为 201
            print("Story posted successfully.")
        except requests.RequestException as e:
            print("Failed to post story:", str(e))

    def get_news(self, command):
        # if not self.logged_in:
        #     print("Please login first.")
        #     return

        # params = {"story_cat": category, "story_region": region, "story_date": date}
        #
        # if agency_id:
        #     params["agency_id"] = agency_id
        #
        # response = requests.get(self.news_service_url + "api/stories", params=params)
        # if response.status_code == 200:
        #     news = response.json().get("stories", [])
        #     for story in news:
        #         print(story)
        # else:
        #     print("Failed to get news:", response.text)
        valid_categories = {'pol', 'art', 'tech', 'trivia'}
        valid_regions = {'uk', 'eu', 'world'}
        valid_params = {'-id', '-cat', '-reg', '-date'}

        if not command.startswith("news"):
            print("Invalid command.")
            return

        params_dict = {"id": "*", "cat": "*", "reg": "*", "date": "*"}

        words = command.split()
        if len(words) > 1:
            params = words[1:]
            for param in params:
                key, value = param.split("=")
                key = key.strip("-")
                print(f"key: {key}, value: {value}")  # 打印参数的 key 和 value，以便调试
                if key == "id":
                    params_dict[key] = value
                    print("ID updated:", params_dict)
                elif key == "cat" and value in valid_categories:
                    params_dict[key] = value
                    print("Category updated:", params_dict)
                elif key == "reg" and value in valid_regions:
                    params_dict[key] = value
                    print("Region updated:", params_dict)
                elif key == "date":
                    params_dict[key] = value
                    print("Date updated:", params_dict)

        print(params_dict)

        if not self.news_service_url:
            self.news_service_url = "http://localhost:8000/api/stories"
            # self.news_service_url = "https://newssites.pythonanywhere.com/api/directory/"
        url = "https://newssites.pythonanywhere.com/api/directory/"
        response = self.session.get(url)
        # print(params_dict)
        # response = self.session.get(url, params=params_dict)
        # # print(response.json())
        # if response.status_code == 200:
        #     news = response.json().get("stories", [])
        #     for story in news:
        #         print(story)
        # else:
        #     print("Failed to get news:", response.text)

        if response.status_code == 200:
            agencies = response.json()
            print(agencies)
        else:
            print("Failed to fetch agencies directory.")
            return
        agencies_list = {}
        for i in agencies:
            name = i['agency_name']
            code = i['agency_code']
            ur = i['url']
            agencies_list[code] = i

        all_stories = []
        if params_dict['id'] == "*":
            for index, agency in enumerate(agencies):  # 使用 enumerate 函数获取索引和值
                try:
                    # print(agency)
                    agency_url = f"{agency['url'].rstrip('/')}/api/stories"
                    print(agency_url, params_dict)
                    stories_response = self.session.get(agency_url, params={
                        "story_cat": params_dict['cat'],
                        "story_region": params_dict['reg'],
                        "story_date": params_dict['date'],
                    })
                    if stories_response.status_code == 200:
                        data = stories_response.json()
                        stories = data.get('stories', [])
                        all_stories.extend(stories)
                        for story in stories:
                            id = story.get('key')
                            headline = story.get('headline')
                            category = story.get('story_cat')
                            region = story.get('story_region')
                            author = story.get('author')
                            date = story.get('story_date')
                            details = story.get('story_details')
                            print(f"Key: {id}")
                            print(f"Headline: {headline}")
                            print(f"Category: {category}")
                            print(f"Region: {region}")
                            print(f"Author: {author}")
                            print(f"Date: {date}")
                            print(f"Details: {details}")
                            print("-" * 40)
                    else:
                        print(f"Error retrieving stories from {agency['url']}: HTTP {stories_response.status_code}")
                except requests.exceptions.ConnectionError as e:
                    print(f"Error connecting to {agency['url']}: {e}")
        elif params_dict['id'] == "local":
            stories_response = self.session.get("http://localhost:8000/api/stories", params={
                "story_cat": params_dict['cat'],
                "story_region": params_dict['reg'],
                "story_date": params_dict['date'],
            })
            print(stories_response.json())
            news = stories_response.json().get("stories")
            if len(news) == 0:
                print("No stories")
            else:
                for story in news:
                    id = story.get('key')
                    headline = story.get('headline')
                    category = story.get('story_cat')
                    region = story.get('story_region')
                    author = story.get('author')
                    date = story.get('story_date')
                    details = story.get('story_details')
                    print(f"Key: {id}")
                    print(f"Headline: {headline}")
                    print(f"Category: {category}")
                    print(f"Region: {region}")
                    print(f"Author: {author}")
                    print(f"Date: {date}")
                    print(f"Details: {details}")
                    print("-" * 40)
        else:
            u = agencies_list[params_dict["id"]]['url']
            print(u)
            stories_response = self.session.get(u + '/api/stories', params={
                "story_cat": params_dict['cat'],
                "story_region": params_dict['reg'],
                "story_date": params_dict['date'],
            })
            print(stories_response.text)
            news = stories_response.json().get("stories")
            if len(news) == 0:
                print("No stories")
            else:
                for story in news:
                    id = story.get('key')
                    headline = story.get('headline')
                    category = story.get('story_cat')
                    region = story.get('story_region')
                    author = story.get('author')
                    date = story.get('story_date')
                    details = story.get('story_details')
                    print(f"Key: {id}")
                    print(f"Headline: {headline}")
                    print(f"Category: {category}")
                    print(f"Region: {region}")
                    print(f"Author: {author}")
                    print(f"Date: {date}")
                    print(f"Details: {details}")
                    print("-" * 40)


        # if news:
        #     for story in news:
        #         id = story.get('key')
        #         headline = story.get('headline')
        #         category = story.get('story_cat')
        #         region = story.get('story_region')
        #         author = story.get('author')
        #         date = story.get('story_date')
        #         details = story.get('story_details')
        #         print(f"Key: {id}")
        #         print(f"Headline: {headline}")
        #         print(f"Category: {category}")
        #         print(f"Region: {region}")
        #         print(f"Author: {author}")
        #         print(f"Date: {date}")
        #         print(f"Details: {details}")
        #         print("-" * 30)
        # else:
        #     print("No stories found.")

    def list_agencies(self):
        response = requests.get(BASE_URL + "directory/")
        if response.status_code == 200:
            agencies_list = response.json()  # 直接将响应内容解析为JSON格式
            for agency in agencies_list:
                print("Agency Name:", agency.get("agency_name"))
                print("URL:", agency.get("url"))
                print("Agency Code:", agency.get("agency_code"))
                print()
        else:
            print("Failed to list agencies:", response.text)

    def delete_story(self, story_key):
        if not self.logged_in:
            print("Please login first.")
            return

        response = self.session.delete(self.news_service_url + f"api/stories/{story_key}")
        if response.status_code == 200:
            print("Story deleted successfully.")
        else:
            print("Failed to delete story:", response.text)


def main():
    client = Client()

    while True:
        command = input("Enter command(login + URL, logout, post, news, list, delete, exit): ")
        if command.startswith("login"):
            url = command.split()[1]
            if url == "local":
                url = "http://localhost:8000/"
            client.login(url)
        elif command == "logout":
            client.logout()
        elif command == "post":
            client.post_story()
        # elif command.startswith("news"):
        #     if not client.news_service_url:
        #         client.news_service_url = "http://localhost:8000/"
        #     if len(command.split()) > 1:
        #         # 用户输入了参数
        #         params = command.split()[1:]
        #         params_dict = {}
        #         for param in params:
        #             key, value = param.split("=")
        #             params_dict[key.strip("-")] = value.strip('"')
        #         if "id" not in params_dict:
        #             params_dict["id"] = "*"
        #         if "cat" not in params_dict:
        #             params_dict["cat"] = "*"
        #         if "reg" not in params_dict:
        #             params_dict["reg"] = "*"
        #         if "date" not in params_dict:
        #             params_dict["date"] = "*"
        #         client.get_news(**params_dict)
        #     else:
        #         # 用户未提供参数
        #         client.get_news()
        elif command.startswith("news"):
            client.get_news(command)
        elif command == "list":
            client.list_agencies()
        elif command.startswith("delete"):
            story_key = command.split()[1]
            client.delete_story(story_key)
        elif command == "exit":
            break
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
