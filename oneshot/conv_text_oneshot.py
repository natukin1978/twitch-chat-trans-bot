import asyncio
import logging
import os
import sys

args = len(sys.argv)
if args <= 1:
    exit(1)

sys.path.append("..")
sys.path.append(".")

import global_value as g

g.app_name = "conv_text_oneshot"
g.base_dir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), os.pardir))

from replace_words_helper import match_replace_word, read_replace_words

# ロガーの設定
logging.basicConfig(level=logging.INFO)

async def main():
    text = sys.argv[1]
    replace_words = read_replace_words()
    text = match_replace_word(replace_words, text)
    print(text)

if __name__ == "__main__":
    asyncio.run(main())
