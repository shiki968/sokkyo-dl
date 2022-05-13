from selenium import webdriver
import time
import requests
from bs4 import BeautifulSoup
import os

# chromeドライバーを起動する時のオプションを設定
def setup():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # ヘッドレスで起動
    options.add_argument('--no-sandbox') # 仮想環境下では、sandboxで起動すると失敗するので無効にする
    options.add_argument('--disable-gpu') # ヘッドレスモードで起動するときに必要
    return options

# 指定された著者の小説リストを取得
def get_novel_id_list(driver):
    title_list = driver.find_elements_by_class_name("works-title")  # elementsは複数
    novel_id_list = []
    for title in title_list:
        novel_id = title.find_element_by_tag_name("a").get_attribute("href").split("=")[1]
        novel_id_list.append(novel_id)
    print("{}本の小説をダウンロードします...".format(len(novel_id_list)))
    return novel_id_list

# 小説リストを元に中身を取得
def fetch_novel(payload):

    novel_url = "http://sokkyo-shosetsu.com/novel.php"
    novel_payload = payload
    r = requests.get(novel_url, params=novel_payload)
    soup = BeautifulSoup(r.text, "html.parser")  # 不正なマークアップをパース(perspective)透視する
    
    # 著者名を取得する
    element = soup.find("div", id="header2")
    author_name = element.find("a").get_text()
    # フォルダ作る
    os.mkdir(author_name)

    contents = soup.find("div", id="contents")  # タグとidを一緒に指定
    contents_body = contents.find("div", id="contents-body")
    works_main = contents_body.find("div", class_='works-main')
    main_title = works_main.find("div", id='works-main-title')
    main_text = works_main.find("div", id='works-main-text')
    # print(main_text.get_text())  # タグが消えるだけA
    # print(main_text.text)  　　　# タグが消えるだけB(Aと同じ)

    contents_head = contents.find("div", id="contents-head")
    info = contents_head.find("div", id="info")
    head_list = info.find_all(class_="contents-head-left-items")

    # ファイルに小説を書き込む
    with open(author_name +"\\"+kigou_henkan(main_title.text.strip())+".txt", "w") as f:
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
    print("{}のダウンロードが完了しました。".format(main_title.text.strip()))

# ファイル名に使用できない文字を書き換える
def kigou_henkan(kigou_ari):
    return kigou_ari.replace("/","／").replace("\\","＼").replace("*","＊").replace("?","？").replace(":","：").replace("<","＜").replace(">","＞").replace("|","｜")


def main():
    try:
        options = setup()
        driver = webdriver.Chrome(options=options)
    except:
        sys.exit("googlechromeの現バージョンに対応したwebdriverがダウンロードされていません")

    # 作者のページをseleniumで表示
    author_url = "http://sokkyo-shosetsu.com/author.php"  # 元のURL
    author_id = "268703397"  # ここにダウンロードしたい著者のidを入れる

    try:
        driver.get("{}?id={}".format(author_url,author_id))
    except:
        sys.exit("ページが見つかりません")
    
    time.sleep(10)

    # 「もっと見る...」ボタンを、表示されなくなるまで押す
    while driver.find_element_by_class_name('more').is_displayed():
        driver.find_element_by_class_name('more').click()
        time.sleep(3)
    
    novel_id_list = get_novel_id_list(driver)

    # 一本ずつtxt形式でダウンロード
    for novel_id in novel_id_list:
        fetch_novel({'id': novel_id})
        time.sleep(2)

# https://www.teradas.net/archives/30474/
# webdriverの自動更新（main.pyと同じフォルダにドライバ入れる）

if __name__ == '__main__':
    main()
