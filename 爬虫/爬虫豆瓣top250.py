import requests
from bs4 import BeautifulSoup
import pandas as pd

# 设置请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 初始化一个空的列表来存储电影信息
movies_data = []

for start_num in range(0, 250, 25):
    # 发送请求时带上headers
    response = requests.get("https://movie.douban.com/top250?start=" + str(start_num), headers=headers)

    # 打印状态码和响应内容，方便调试
    print(f"状态码: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')

    # 找到所有电影信息的div
    items = soup.find_all('div', class_='item')

    # 提取每个电影的信息
    for item in items:
        title_tag = item.find('span', class_='title')
        if title_tag and '/' not in title_tag.string:
            movie_title = title_tag.string

            # 提取评分
            rating_tag = item.find('span', class_='rating_num')
            rating = rating_tag.string

            # 提取评价人数
            rating_div = item.find('span', class_='rating_num').parent  # 找到评分所在的div
            spans = rating_div.find_all('span')
            rating_people = spans[-1].string  # 最后一个span包含评价人数

            # 提取评论内容
            comment_tag = item.find('p', class_='quote')
            if comment_tag:  # 先检查是否找到了 p class='quote'
                comment_span = comment_tag.find('span')
                comment = comment_span.string if comment_span else 'N/A'
            else:
                comment = 'N/A'

            # 提取电影信息
            bd_tag = item.find('div', class_='bd')
            movie_info = bd_tag.get_text().strip() if bd_tag else 'N/A'

            # 添加到列表
            movies_data.append({
                'Title': movie_title,
                'Info': movie_info,
                'Rating': rating,
                'Rating People': rating_people,
                'Comment': comment
            })



# 创建DataFrame
df = pd.DataFrame(movies_data)

# 打印DataFrame
df.to_csv('movies_data.csv', index=False)