from datetime import datetime
from pathlib import Path
import sys
import tkinter as tk
import tkinter.font as tf
import tkinter.ttk as ttk
import tkinter.messagebox as mb
from traceback import format_exc
from webbrowser import open_new_tab

import request


class Widget:
    columns = ['제목', '링크', '사이트', '작성시간']
    dict_width = {
        '제목': 450,
        '사이트': 150,
        '작성시간': 150,
    }
    list_item = []
    open_link = False
    dt = datetime.now()

    def __init__(self, window: tk.Tk):
        window.wm_title('핫딜 정보 RSS 리더기')
        self.window = window

        frame = tk.Frame(window)
        frame.grid(column=0, row=0, sticky='n')

        frame_a = tk.Frame(frame)
        frame_a.grid(column=0, row=0, sticky='ewsn')
        self.set_input(frame_a)

        frame_b = tk.Frame(frame)
        frame_b.grid(column=0, row=1, sticky='ewsn')
        self.set_treeview(frame_b)
        self.path_err = Path(sys.argv[-1]).parent / 'err.txt'

        return

    def err(self):
        with open(self.path_err, 'w', encoding='utf-8') as txt:
            txt.write(format_exc())
        return

    def request(self):
        self.status.set('메세지 : RSS를 가져오는 중..')

        now = datetime.now()
        is_update = False
        if self.list_item and (now - self.dt).seconds < 60:
            item_list = self.list_item
        else:
            try: item_list = request.get()
            except:
                self.err()
                self.status.set('메세지 : RSS를 가져오는데 실패했습니다!')
                mb.showerror('에러', 'err.txt를 확인해주세요.')
                return
            is_update = True
            self.dt = now
            self.time_request.set(f"갱신시간 : {self.dt.strftime('%Y-%m-%d %H:%M:%S')}")
            self.list_item = item_list

        self.tv.delete(*self.tv.get_children())
        keyword = self.keyword.get().strip()
        list_keyword = keyword.upper().split()
        list_item = []
        for i in item_list:
            title = i['제목'].upper()
            if list_keyword and all(i not in title for i in list_keyword): continue
            list_item.append(i)
        if not list_item:
            if keyword: self.status.set(f'메세지 : RSS에서 "{keyword}" 단어를 찾을 수 없습니다!')
            else:
                if is_update: self.status.set(f'메세지 : RSS를 가져왔으나, 아무것도 찾을 수 없습니다!')
                else: self.status.set('메세지 : 아직 RSS를 갱신할 수 없습니다. 잠시 후에 다시 요청해주세요.')
        elif keyword: self.status.set(f'메세지 : "{keyword}" 단어가 포함된 RSS를 찾았습니다!')
        else:
            if is_update: self.status.set('메세지 : 핫딜 RSS를 가져왔습니다!')
            else: self.status.set('메세지 : 아직 RSS를 갱신할 수 없습니다. 잠시 후에 다시 요청해주세요.')
        self.insert_treeview(list_item)
        return

    def insert_treeview(self, list_item):
        self.tv.delete(*self.tv.get_children())
        for i in list_item:
            self.tv.insert('', 'end', values=[i[k] for k in self.columns])
        return

    def change_open_link(self):
        return setattr(self, 'open_link', (self.bv_open_link.get()))

    def set_input(self, frame: tk.Frame):
        tk.Label(frame, text='탐색 키워드 :').grid(column=0, row=0, sticky='w')
        self.keyword = tk.StringVar()
        en_keyword = tk.Entry(frame, textvariable=self.keyword)
        en_keyword.grid(column=1, row=0, sticky='w')
        en_keyword.bind('<Return>', lambda *x: self.request())
        tk.Label(frame, text=' ' * 50).grid(column=2, row=0)
        tk.Button(frame, text='핫딜 RSS 가져오기', command=self.request, cursor='hand2').grid(column=3, row=0)
        self.bv_open_link = tk.BooleanVar(value=self.open_link)
        tk.Checkbutton(frame, text='클릭시 링크 열기', variable=self.bv_open_link,
            command=lambda *x: self.change_open_link(), cursor='hand2').grid(column=3, row=1)
        self.status = tk.StringVar(value='메세지 : RSS 가져오기 버튼을 눌러보세요!')
        tk.Label(frame, textvariable=self.status).grid(column=0, row=1, columnspan=3, sticky='w')

        self.time_request = tk.StringVar(value='갱신시간 : -')
        tk.Label(frame, textvariable=self.time_request).grid(column=0, row=3, columnspan=2, sticky='w')
        return

    def order_treeview(self, name=None, reverse=False):
        tv = self.tv
        item_list = self.list_item
        if not item_list: return

        self.bv_open_link.set(False)
        self.change_open_link()

        keyword = self.keyword.get()
        list_keyword = keyword.upper().split()
        list_item = [i for i in item_list if all([k in i['제목'].upper() for k in list_keyword])] if keyword else item_list
        item_sorted = sorted(list_item, key=lambda x: (x[name]), reverse=reverse)
        self.insert_treeview(item_sorted)

        text = f"{name} " + ('△' if reverse else '▽')
        for i in tv['columns']: tv.heading(i, text=f'{i}    ', command=lambda x=i: self.order_treeview(x, False))
        tv.heading(name, text=text, command=lambda x=name: self.order_treeview(x, (not reverse)))
        sort = '오름차순' if reverse else '내림차순'
        self.status.set(f'메세지 : "{name}" 항목을 기준으로 {sort} 정렬했습니다!')
        return

    def select_treeview(self):
        tv, open_link = (self.tv, self.open_link)
        if not open_link: return
        # print(f'{open_link=}')
        key = tv.selection()[0]
        link = tv.set(key, '링크')
        # print(f'{link=}')
        open_new_tab(link)
        return

    def set_treeview(self, frame: tk.Frame):
        self.tv = ttk.Treeview(frame, show='headings', height=35, columns=self.columns, displaycolumns=[i for i in self.columns if i != '링크'])
        self.tv.bind('<<TreeviewSelect>>', lambda *_: self.select_treeview())
        self.tv.grid(column=0, row=0, sticky='ewsn',)

        for i in self.columns:
            self.tv.heading(i, text=f'{i}    ', command=lambda x=i: self.order_treeview(x, False))
            width = self.dict_width.get(i)
            if width: self.tv.column(i, width=width, minwidth=width)

        scroll = tk.Scrollbar(frame, orient='vertical', command=self.tv.yview,)
        scroll.grid(column=1, row=0, sticky='esn',)
        self.tv.config(yscrollcommand=scroll.set)
        return


def run():
    window = tk.Tk()
    fc = tf.nametofont('TkDefaultFont')
    fc.configure(size=10)
    Widget(window)
    window.update()
    width, height = (window.winfo_width(), window.winfo_height())
    # print(f'{(width, height)=}')
    window.wm_minsize(width=width, height=height+20)
    window.resizable(False, False)
    window.mainloop()
    return


def main():
    run()
    return


if __name__ == '__main__':
    main()

