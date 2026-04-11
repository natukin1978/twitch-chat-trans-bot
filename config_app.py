import os
import subprocess
import sys
import webbrowser
from threading import Timer

import twitchio
import uvicorn
from fastapi import Body, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import global_value as g
from config_helper import read_config, read_json, write_config
from json_editor_helper import sort_dict_by_schema
from resource_helper import get_resource_path
from socket_helper import get_free_port

g.app_name = "config_app"
g.base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

app = FastAPI()
app.mount("/images", StaticFiles(directory="images", html=True), name="images")
templates = Jinja2Templates(directory=get_resource_path("templates"))

CONFIG_FILE = "config.json"
SCHEMA_FILE = "schema.json"

HOST = "127.0.0.1"
PORT = get_free_port()

g.schema_data = {}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # 画面表示時に現在の設定とスキーマを読み込む
    config_data = read_config(CONFIG_FILE)
    schema_data = read_json(get_resource_path(SCHEMA_FILE))
    if schema_data:
        g.schema_data = schema_data

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "config": config_data,
            "schema": schema_data,
        },
    )

@app.post("/save")
async def save_config(data: dict):
    # 編集されたデータを保存
    message = ""
    try:
        data = sort_dict_by_schema(data, g.schema_data)
        write_config(data, CONFIG_FILE)

        message = "保存しました"
    except TypeError as e:
        # データにJSON変換できない型（オブジェクトなど）が含まれている場合
        message = f"失敗: JSONに変換できないデータが含まれています。 {e}"

    except OSError as e:
        # 権限不足、ディスク容量不足、無効なパスなど、ファイル操作自体のエラー
        message = f"失敗: ファイルの書き込み中にエラーが発生しました。 {e}"

    except Exception as e:
        # その他の予期せぬエラー
        message = f"失敗: 予期せぬエラーが発生しました。 {e}"

    return {"message": message}

@app.get("/select_file")
async def select_file():
    # plyer, tkinter どちらもダメだったので苦肉の策

    # PowerShellのコマンドを作成（ファイル選択ダイアログを表示してパスを返す）
    cmd = (
        "Add-Type -AssemblyName System.Windows.Forms; "
        "$f = New-Object System.Windows.Forms.OpenFileDialog; "
        "$f.Filter = 'CSV files (*.csv)|*.csv|All files (*.*)|*.*'; "
        "$f.Title = 'users.csv を選択してください'; "
        "$w = New-Object System.Windows.Forms.Form; "
        "$w.TopMost = $true; "
        "$f.ShowDialog($w) | Out-Null; "
        "$f.FileName"
    )

    try:
        # PowerShellを実行
        result = subprocess.run(
            ["powershell", "-Command", cmd],
            capture_output=True,
            text=True,
            encoding="cp932" # Windowsの日本語環境に対応
        )
        # 出力されたパスを取得（改行を削除）
        selected_path = result.stdout.strip()
    except Exception as e:
        print(f"Error: {e}")
        selected_path = ""

    return {"path": selected_path}

@app.post("/get_ids")
async def get_twitch_ids(data: dict = Body(...)):
    client_id = data.get("clientId")
    client_secret = data.get("clientSecret")
    bot_name = data.get("bot", {}).get("name")
    owner_name = data.get("owner", {}).get("name")

    try:
        async with twitchio.Client(
            client_id=client_id, client_secret=client_secret
        ) as client:
            await client.login()

            bot_user, owner_user = await client.fetch_users(
                logins=[bot_name, owner_name]
            )

            return {
                "bot_id": bot_user.id,
                "owner_id": owner_user.id,
            }
    except Exception:
        return None

def open_browser():
    webbrowser.open(f"http://{HOST}:{PORT}")

if __name__ == "__main__":
    # 1秒後にブラウザを開く予約（uvicornの起動待ち）
    Timer(1, open_browser).start()

    uvicorn.run(app, host=HOST, port=PORT)
