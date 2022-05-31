import PySimpleGUI as sg
import main
import threading

sg.theme('DarkTeal7')  # デザインテーマの設定

# ウィンドウに配置するコンポーネント
layout = [  [sg.Text('著者のidを入力して下さい（著者ページURLの「?id= 」以降の数字）')],
            [sg.Text('id', size = (7, 1)), sg.InputText('3250591982')],
            [sg.Text('保存先',size = (7, 1)), sg.InputText(), sg.FolderBrowse('保存先フォルダを選択', key='inputFilePath')],
            [sg.Button(button_text = 'ダウンロード開始')],
            [sg.Output(size=(80,20))]
        ]

# ウィンドウの生成
window = sg.Window('即興小説をまとめて保存', layout)

# イベントループ
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break

    elif event == 'ダウンロード開始':
        # print('あなたが入力した値： ', values[0])
        if values[0] == "":
            print("idを入力して下さい")
        if values[1] == "":
            print("「保存先フォルダを選択」ボタンを押して、保存先を入力して下さい")
        if values[0] != "" and values[1] != "":
            threading.Thread(target=main.main, args=(values[0],values[1]), daemon=True).start()
            # main.main(values[0],values[1])

    # elif event == 'キャンセル':
    #     exit()


window.close()
