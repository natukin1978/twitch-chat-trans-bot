import os
import sys
import webbrowser
from threading import Timer

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import global_value as g
from config_helper import read_config, read_json, write_config

g.app_name = "detail_config_app"
g.base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

from json_editor_helper import sort_dict_by_schema
from resource_helper import get_resource_path
from socket_helper import get_free_port

app = FastAPI()
app.mount("/images", StaticFiles(directory="images", html=True), name="images")
templates = Jinja2Templates(directory=get_resource_path("templates"))

HONORIFICS_FILE = "honorifics.json"
EXCLUDEWORDS_FILE = "exclude_words.json"
REPLACEWORDS_FILE = "replace_words.json"
VOICE_FILE = "voice.json"
RENAMEMAP_FILE = "rename_map.json"
VOICEMAP_FILE = "voice_map.json"

SCHEMA_FILE = "detail_schema.json"

HOST = "127.0.0.1"
PORT = get_free_port()

g.schema_data = {}
g.bot = None
g.config = None

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # 画面表示時に現在の設定とスキーマを読み込む
    config_data = {
        HONORIFICS_FILE: read_config(HONORIFICS_FILE),
        EXCLUDEWORDS_FILE: read_config(EXCLUDEWORDS_FILE),
        REPLACEWORDS_FILE: read_config(REPLACEWORDS_FILE),
        VOICE_FILE: read_config(VOICE_FILE),
        RENAMEMAP_FILE: read_config(RENAMEMAP_FILE),
        VOICEMAP_FILE: read_config(VOICEMAP_FILE),
    }
    schema_data = read_json(get_resource_path(SCHEMA_FILE))
    if schema_data:
        g.schema_data = schema_data

    return templates.TemplateResponse(
        request=request,
        name="detail_config.html",
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
        write_config(data[HONORIFICS_FILE], HONORIFICS_FILE)
        write_config(data[EXCLUDEWORDS_FILE], EXCLUDEWORDS_FILE)
        write_config(data[REPLACEWORDS_FILE], REPLACEWORDS_FILE)
        write_config(data[VOICE_FILE], VOICE_FILE)
        write_config(data[RENAMEMAP_FILE], RENAMEMAP_FILE)
        write_config(data[VOICEMAP_FILE], VOICEMAP_FILE)

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
def open_browser():
    webbrowser.open(f"http://{HOST}:{PORT}")

if __name__ == "__main__":
    # 1秒後にブラウザを開く予約（uvicornの起動待ち）
    Timer(1, open_browser).start()

    uvicorn.run(app, host=HOST, port=PORT)
