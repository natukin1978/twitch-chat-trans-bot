import asyncio
import os
import subprocess
import sys
import webbrowser
from threading import Timer

import asqlite
import twitchio
import uvicorn
from fastapi import Body, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import constants
import global_value as g
from config_helper import read_config, read_json, write_config

g.app_name = "config_app"
g.base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

from json_editor_helper import sort_dict_by_schema
from resource_helper import get_resource_path
from socket_helper import get_free_port
from twitch_bot import (
    TwitchBot,
    setup_database,
)

app = FastAPI()
app.mount("/images", StaticFiles(directory="images", html=True), name="images")
templates = Jinja2Templates(directory=get_resource_path("templates"))
templates.env.globals.update(
    CALLBACK_URL_BOT=constants.CALLBACK_URL_BOT,
    CALLBACK_URL_OWNER=constants.CALLBACK_URL_OWNER,
)

CONFIG_FILE = "config.json"
SCHEMA_FILE = "schema.json"

HOST = "127.0.0.1"
PORT = get_free_port()

g.schema_data = {}
g.bot = None
g.config = None

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # 画面表示時に現在の設定とスキーマを読み込む
    config_data = read_config(CONFIG_FILE)

    # 項目に無い設定を追加
    if "enable" not in config_data["assistantSeika"]:
        config_data["assistantSeika"]["enable"] = bool(config_data["assistantSeika"]["baseUrl"])

    schema_data = read_json(get_resource_path(SCHEMA_FILE))
    if schema_data:
        g.schema_data = schema_data

    await close_callback()
    asyncio.create_task(boot_callback())

    return templates.TemplateResponse(
        request=request,
        name="config.html",
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

        await close_callback()
        asyncio.create_task(boot_callback())

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

    # ダイアログを最前面に持ってくるためのPowerShellスクリプト
    cmd = (
        "Add-Type -AssemblyName System.Windows.Forms; "
        "$f = New-Object System.Windows.Forms.OpenFileDialog; "
        "$f.Filter = 'CSV files (*.csv)|*.csv|All files (*.*)|*.*'; "
        "$f.Title = 'users.csv を選択してください'; "

        # 画面外に見えないダミーフォームを作成し、それを最前面に固定
        "$w = New-Object System.Windows.Forms.Form; "
        "$w.StartPosition = 'Manual'; "
        "$w.Location = New-Object System.Drawing.Point(-500, -500); " # 画面外へ
        "$w.Size = New-Object System.Drawing.Size(1, 1); "
        "$w.TopMost = $true; "

        # フォームを表示して即座にアクティブ化
        "$w.Show(); "
        "$w.Activate(); "

        # ダミーフォームを親としてダイアログを表示
        "$res = $f.ShowDialog($w); "
        "$w.Close(); "

        # パスを返す
        "if($res -eq 'OK'){ $f.FileName }"
    )

    try:
        result = subprocess.run(
            ["powershell", "-WindowStyle", "Hidden", "-Command", cmd], # PowerShell自体の黒い窓も隠す
            capture_output=True,
            text=True,
            encoding="cp932"
        )
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

@app.get("/close_callback")
async def close_callback():
    if g.bot:
        await g.bot.close()
        g.bot = None

@app.get("/boot_callback")
async def boot_callback():
    g.config = read_config(CONFIG_FILE)

    conf_tw = g.config["twitch"]
    if not conf_tw["clientId"] or not conf_tw["clientSecret"] or not conf_tw["bot"]["id"] or not conf_tw["owner"]["id"]:
        return

    async with asqlite.create_pool("tokens.db") as tdb:
        tokens, subs = await setup_database(tdb)

        g.bot = TwitchBot(token_database=tdb, subs=subs)
        for pair in tokens:
            await g.bot.add_token(*pair)

        await g.bot.start(load_tokens=False)


def open_browser():
    webbrowser.open(f"http://{HOST}:{PORT}")

if __name__ == "__main__":
    # 1秒後にブラウザを開く予約（uvicornの起動待ち）
    Timer(1, open_browser).start()

    uvicorn.run(app, host=HOST, port=PORT)
