from bs4 import BeautifulSoup
from dateutil.parser import parse
import requests


s = requests.Session()

tuple_url = (
    ('루리웹 - 핫딜게시판', 'https://bbs.ruliweb.com/market/board/1020/rss'),
    ('뽐뿌 - 뽐뿌게시판', 'https://www.ppomppu.co.kr/rss.php?id=ppomppu'),
    ('쿨앤조이 - 지름/알뜰정보', 'https://coolenjoy.net/bbs/rss.php?bo_table=jirum'),
)

def get():
    list_item: list[dict[str, str]] = []
    for name, url in tuple_url:
        try: r = s.get(url)
        except: raise Exception(f'request failure.\nstatus: {r.status_code}\nname: {name}\nurl: {url}')
        soup = BeautifulSoup(r.text, 'xml')
        item_list = soup.select('item')
        for item in item_list:
            title = item.find('title')
            link = item.find('link')
            Time = item.find('pubDate')
            if not Time: Time = item.find('dc:date')
            dt = parse(Time.text)
            i = {
                '작성시간': dt.strftime('%Y-%m-%d %H:%M:%S'),
                '사이트': name,
                '링크': link.text,
                '제목': title.text,
            }
            list_item.append(i)

    return list_item


if __name__ == '__main__':
    list_item = get()
    for n, i in enumerate(list_item, 1):
        print(f'  {(n, i)}')