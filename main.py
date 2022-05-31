from selenium import webdriver
import time
import requests
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import os

def setup():
    # chromeドライバーを起動する時のオプションを設定
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # ヘッドレスで起動
    options.add_argument('--no-sandbox') # 仮想環境下では、sandboxで起動すると失敗するので無効にする
    options.add_argument('--disable-gpu') # ヘッドレスモードで起動するときに必要
    options.add_experimental_option('excludeSwitches', ['enable-logging'])  # エラーメッセージを消す
    return options

def get_novel_id_list(driver):
	# 著者の小説のリストを取得
    title_list = driver.find_elements(By.CLASS_NAME,"works-title")  # elementsは複数
    novel_id_list = []
    for title in title_list:
        novel_id = title.find_element(By.TAG_NAME,"a").get_attribute("href").split("=")[1]
        novel_id_list.append(novel_id)
    print("{}本の小説をダウンロードします...（予定時間{}秒）".format(len(novel_id_list), len(novel_id_list)*4))
    print("")
    return novel_id_list


def fetch_novel(novel_id, folder):

    novel_url = "http://sokkyo-shosetsu.com/novel.php"
    r = requests.get("{}?id={}".format(novel_url, novel_id))

    # Beautiful Soupでhtmlを取得
    soup = BeautifulSoup(r.text, "html.parser")  # 不正なマークアップをパース(perspective)透視する
    contents = soup.find("div", id="contents")  # タグとidを一緒に指定
    contents_body = contents.find("div", id="contents-body")
    works_main = contents_body.find("div", class_="works-main")
    # print(contents_body)
    main_title = works_main.find("div", id="works-main-title")
    main_text = works_main.find("div", id="works-main-text")

    contents_head = contents.find("div", id="contents-head")
    info = contents_head.find("div", id="info")
    head_list = info.find_all(class_="contents-head-left-items")

    with open(folder  + "/"+kigou_henkan(main_title.text.strip())+".txt", "w", encoding='UTF-8') as f:
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
                text = "  " + text.strip()
            text = text.rstrip("        ")
            f.write(text)
        f.write("\n")
    print("「{}」のダウンロードが完了しました。".format(main_title.text.strip()))

def kigou_henkan(kigou_ari):
    return kigou_ari.replace("/","／").replace("\\","＼").replace("*","＊").replace("?","？").replace(":","：").replace("<","＜").replace(">","＞").replace("|","")

# def make_folder(r, folder):

#     # Beautiful Soupでhtmlを取得
#     soup = BeautifulSoup(r.text, "html.parser")  # 不正なマークアップをパース(perspective)透視する
#     contents = soup.find("div", id="contents")  # タグとidを一緒に指定
#     contents_head = contents.find("div", id="contents-head")
#     author_link = contents_head.find("div", id='header2')
#     author_name = author_link.find("a").get_text()
#     author_name = kigou_henkan(author_name)
#     new_dir_path = folder + "/" + author_name

#     # すでにファイルが存在したら？
#     try:
#         os.mkdir(new_dir_path)
#     except:
#         print("フォルダが作れませんでした")
    
#     return author_name



def main(id, folder):
    options = setup()

    # 作者のページをseleniumで表示（ボタンがjsなので）
    author_url = "http://sokkyo-shosetsu.com/author.php"  # 元のURL
    # author_id = "268703397"  # ここにダウンロードしたい著者のidを入れる
    # author_id = "345244873"  # ここにダウンロードしたい著者のidを入れる
    # author_id = "345244874444444444444"  # ここにダウンロードしたい著者のidを入れる
    author_id = id
    # idは数字のみにする
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    try:
        driver.get("{}?id={}".format(author_url,author_id))  # idが存在しないときはTopページにアクセスする
    except:
        print("著者ページにアクセスできません")

    waiting_time = 3

    # 「もっと見る...」ボタンを、表示されなくなるまで押す
    try:
        print("......作品ページのURLを取得しています......")
        while driver.find_element(By.CLASS_NAME,'more').is_displayed():
            driver.find_element(By.CLASS_NAME,'more').click()
            time.sleep(waiting_time)
    except:
        print("著者ページにアクセスできません。idを正しく入力して下さい")
        return

    novel_id_list = get_novel_id_list(driver)
    # os.mkdir(folder)

    # Requestsでwebページを取得
    # r = requests.get("{}?id={}".format(author_url,author_id))
    # author_name = make_folder(r, folder)

	#  取得したURLを使い、一本ずつtxt形式でダウンロード
    waiting_time = 2
    for novel_id in novel_id_list:
        fetch_novel(novel_id, folder)
        time.sleep(waiting_time)

    print("\nすべてダウンロードしました。")

# 途中で止めたいときは？


if __name__ == '__main__':
    main()
