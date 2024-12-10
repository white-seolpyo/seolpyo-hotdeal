import json
from pathlib import Path
from traceback import format_exc

import request, message

path_dir = Path(__file__).parent
path_log = (path_dir / 'log.txt')


def run():
    try:
        with open(path_log, 'r', encoding='utf-8') as txt:
            set_log = set(json.loads(txt.read()))
    except: set_log = set()

    item_list = request.get()
    list_item, list_new = ([], [])
    keyword_list = ['햇반', '참치', '스팸', 'spam', '리챔', '만두', '교자',]
    list_keyword = [i.upper() for i in keyword_list]
    for item in item_list:
        list_new.append(item['링크'])
        if item['링크'] in set_log: continue
        title = item['제목'].upper()
        if all([i not in title for i in list_keyword]): continue
        list_item.append(item)

    text_list = []
    for n, i in enumerate(list_item, 1):
        text = f"""{n}. <a href="{i['링크']}">{i['제목']}</a> [{i['사이트']}]"""
        text_list.append(text)

    list_text, step = ([], 5)
    for n, i in enumerate(text_list[::step]):
        s = n * step
        e = s + step
        list_text.append('\n\n'.join(text_list[s:e]))

    for text in list_text: message.send(text)

    with open(path_log, 'w', encoding='utf-8') as txt:
        json.dump(list_new, txt, indent='  ',)


def main():
    try: run()
    except: message.err(format_exc())


if __name__ == '__main__':
    main()

