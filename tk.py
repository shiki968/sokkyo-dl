from tkinter import *
from tkinter import ttk
from selenium import webdriver
import time
import requests
from bs4 import BeautifulSoup


# tkはwebアプリにはできない。

# ボタンを押したときの処理 --- (*1)
def start_main():
    # 史季のページをseleniumで表示
    author_url = "http://sokkyo-shosetsu.com/author.php"
    # author_id = '268703397'
    author_id = str(text_id.get())
    driver = webdriver.Chrome()
    driver.get("{}?id={}".format(author_url,author_id))

    time.sleep(10)

    try:
        # 「もっと見る...」ボタンを、表示されなくなるまで押す
        while driver.find_element_by_class_name('more').is_displayed():
            driver.find_element_by_class_name('more').click()
            time.sleep(3)
    except:
        #ボタンがないときの処理
        pass

    title_list = driver.find_elements_by_class_name("works-title")  # elementsは複数
    novel_id_list = []
    for title in title_list:
        novel_id = title.find_element_by_tag_name("a").get_attribute("href").split("=")[1]
        novel_id_list.append(novel_id)
    # print("{}本の小説をダウンロードします...".format(len(novel_id_list)))
    result_text.set(str(len(novel_id_list)) + "本の小説をダウンロードします...")

    for novel_id in novel_id_list:
        fetch_novel({'id': novel_id})
        time.sleep(2)

    result_text.set(str(len(novel_id_list)) + "本のダウンロードが完了しました...")


def fetch_novel(payload):

    novel_url = "http://sokkyo-shosetsu.com/novel.php"
    novel_payload = payload
    r = requests.get(novel_url, params=novel_payload)

    soup = BeautifulSoup(r.text, "html.parser")  # 不正なマークアップをパース(perspective)透視する
    contents = soup.find("div", id="contents")  # タグとidを一緒に指定
    contents_body = contents.find("div", id="contents-body")
    works_main = contents_body.find("div", class_='works-main')
    main_title = works_main.find("div", id='works-main-title')
    main_text = works_main.find("div", id='works-main-text')

    contents_head = contents.find("div", id="contents-head")
    info = contents_head.find("div", id="info")
    head_list = info.find_all(class_="contents-head-left-items")

    with open("novel\\"+kigou_henkan(main_title.text.strip())+".txt", "w") as f:

        # 必須要素など
        for head in head_list:
            # pprint(head.__dict__)
            f.write(head.get_text().replace(" ", "")+" ")
        f.write("\n\n")

        # 本文
        for i, text in enumerate(main_text.childGenerator()):
            if text.name == "br":  # <br/>はtag。文字列ではない
                text = "\n"
            if i == 0:
                text = "　" + text.strip()
            text = text.rstrip("        ")
            f.write(text)
        f.write("\n")
    # print("{}のダウンロードが完了しました。".format(main_title.text.strip()))


def kigou_henkan(kigou_ari):
    # return kigou_ari.translate(str.maketrans({'/': '／', '\\': 'T'})))
    return kigou_ari.replace("/","／").replace("\\","＼").replace("*","＊").replace("?","？").replace(":","：").replace("<","＜").replace(">","＞").replace("|","")


# ウィンドウを作成 --- (*2)
root = Tk()
root.title('u即興小説の保存')
root.geometry("450x200")

# ウィジェットの作成
frame1 = ttk.Frame(root, padding=16)
label1 = ttk.Label(frame1, text='著者のid:')
t = StringVar()
entry1 = ttk.Entry(frame1, textvariable=t)
button1 = ttk.Button(
    frame1,
    text='ダウンロード',
    command=lambda: start_main)

# レイアウト
frame1.pack()
label1.pack(side=LEFT)
entry1.pack(side=LEFT)
button1.pack(side=LEFT)

# Frame
#frame1 = ttk.Frame(root, padding=10)
#frame1.grid(sticky=(N, W, S, E))
#frame1.columnconfigure(0, weight=1);
#frame1.rowconfigure(0, weight=1);

 # プログレスバー (確定的)
pbval = IntVar(value=3)
pb = ttk.Progressbar(
    frame1,
    orient=HORIZONTAL,
    variable=pbval,
    maximum=10,
    length=200,
    mode='determinate')
#pb.grid(row=0, column=0, sticky=(N, E, S, W))

# ウィンドウを動かす
root.mainloop()
