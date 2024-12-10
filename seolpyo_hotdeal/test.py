from seolpyo_hotdeal import request, message


list_text = []
list_item = request.get()
for n, i in enumerate(list_item, 1):
    if len(list_text) == 5:
        message.send('\n\n'.join(list_text))
        list_text.clear()
    text = f"""{n}. <a href="{i['링크']}">[{i['사이트']}] {i['제목']}</a>"""
    list_text.append(text)

if list_text: message.send('\n\n'.join(list_text))



