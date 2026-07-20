import logging
import re
import time
from typing import TYPE_CHECKING

import asqlite
import langdetect
import twitchio
from twitchio import eventsub
from twitchio.ext import commands

if TYPE_CHECKING:
    import sqlite3


import global_value as g
from exclude_words_helper import match_exclude_word, read_exclude_words
from replace_words_helper import match_replace_word, read_replace_words
from talk_voice import talk_voice
from translate_helper import get_use_nickname, talk_voice_with_nickname, translate
from voice_map_helper import get_cid, read_voice_map

logger = logging.getLogger(__name__)


class TwitchBot(commands.AutoBot):
    def __init__(
        self, *, token_database: asqlite.Pool, subs: list[eventsub.SubscriptionPayload]
    ) -> None:
        self.token_database = token_database

        ctw = g.config["twitch"]
        super().__init__(
            client_id=ctw["clientId"],
            client_secret=ctw["clientSecret"],
            bot_id=ctw["bot"]["id"],
            owner_id=ctw["owner"]["id"],
            prefix="!",
            subscriptions=subs,
            force_subscribe=True,
        )

    async def setup_hook(self) -> None:
        # Add our component which contains our commands...
        await self.add_component(MyComponent(self))

    async def event_oauth_authorized(
        self, payload: twitchio.authentication.UserTokenPayload
    ) -> None:
        # トークン情報（アクセストークン／リフレッシュトークン）のデータベース更新のみ行います。
        # 自分のチャンネル専用BOTのため、ここでの二重の購読登録（multi_subscribe）は行いません。
        await self.add_token(payload.access_token, payload.refresh_token)

    async def add_token(
        self, token: str, refresh: str
    ) -> twitchio.authentication.ValidateTokenPayload:
        # Make sure to call super() as it will add the tokens interally and return us some data...
        resp: twitchio.authentication.ValidateTokenPayload = await super().add_token(
            token, refresh
        )

        # Store our tokens in a simple SQLite Database when they are authorized...
        query = """
        INSERT INTO tokens (user_id, token, refresh)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET
            token = excluded.token,
            refresh = excluded.refresh;
        """

        async with self.token_database.acquire() as connection:
            await connection.execute(query, (resp.user_id, token, refresh))

        logger.info("Added token to the database for user: %s", resp.user_id)
        return resp

    async def event_ready(self) -> None:
        bot = self.user
        logger.info("Successfully logged in as: %s (%s)", bot.display_name, bot.name, extra={"force": True})
        owner_user = self.owner
        g.owner_attr = {
            "id": owner_user.id,
            "name": owner_user.name,
            "display_name": owner_user.display_name,
            "description": owner_user.description,
        }

    def get_owner_partial_user(self) -> twitchio.PartialUser:
        return self.create_partialuser(user_id=self.owner_id)

    async def send_message(self, message: str) -> None:
        owner_user = self.get_owner_partial_user()
        await owner_user.send_message(sender=self.bot_id, message=message)

    async def send_shoutout(self, target_name: str) -> None:
        owner_user = self.get_owner_partial_user()
        target_user = await self.fetch_user(login=target_name)
        await owner_user.send_shoutout(
            moderator=self.bot_id,
            to_broadcaster=target_user,
        )

    async def ban_user(self, target_name: str) -> twitchio.Ban:
        owner_user = self.get_owner_partial_user()
        target_user = await self.fetch_user(login=target_name)
        return await owner_user.ban_user(
            moderator=self.bot_id,
            user=target_user,
            reason="disrupted the broadcast.",
        )

    async def timeout_user(self, target_name: str, duration: int) -> twitchio.Timeout:
        owner_user = self.get_owner_partial_user()
        target_user = await self.fetch_user(login=target_name)
        return await owner_user.timeout_user(
            moderator=self.bot_id,
            user=target_user,
            duration=duration,
            reason="disrupted the broadcast.",
        )


class MyComponent(commands.Component):
    # An example of a Component with some simple commands and listeners
    # You can use Components within modules for a more organized codebase and hot-reloading.

    def __init__(self, bot: TwitchBot) -> None:
        # Passing args is not required...
        # We pass bot here as an example...
        self.bot = bot
        self.prev_nickname = ""

    # An example of listening to an event
    # We use a listener in our Component to display the messages received.
    @commands.Component.listener()
    async def event_message(self, payload: twitchio.ChatMessage) -> None:
        await self.event_base_message(payload)

    @commands.Component.listener()
    async def event_chat_notification(self, payload: twitchio.ChatNotification) -> None:
        await self.event_base_message(payload)

    async def event_base_message(self, payload: twitchio.ChatMessage | twitchio.ChatNotification) -> None:
        # BOT自身のメッセージは読み上げ・翻訳しない
        if payload.chatter.id == self.bot.bot_id:
            return

        combined_parts = []
        for fragment in payload.fragments:
            if fragment.type == "text":
                # 普通のコメ
                text = fragment.text.strip()
                if text:
                    combined_parts.append(text)

            elif fragment.type == "emote":
                # Twitchスタンプは括弧で囲んで表現
                raw_text = fragment.text
                clean_text = re.sub(r"^[^A-Z]*", "", raw_text)
                display_text = clean_text if clean_text else raw_text
                combined_parts.append(f"({display_text})")

        if hasattr(payload, "system_message") and payload.system_message:
            logger.info(payload.system_message, extra={"force": True})
            combined_parts.append(f"({payload.system_message})")

        text = " ".join(combined_parts)
        if text.startswith("/"):
            # モデレーターコマンドはスキップ
            return

        user = payload.chatter.display_name
        cid = get_cid(read_voice_map(), user)
        nickname = get_use_nickname(user)

        if not text:
            # 本文が無い場合でも名前だけは読み上げる
            await talk_voice(nickname, cid)
            return

        if self.prev_nickname == nickname:
            # 直前と同じ人の名前は省略する
            nickname = ""
        else:
            self.prev_nickname = nickname

        replace_words = read_replace_words()
        text = match_replace_word(replace_words, text)

        exclude_words = read_exclude_words()
        if match_exclude_word(exclude_words, text):
            # 除外キーワードなので翻訳しない
            await talk_voice_with_nickname(nickname, text, cid)
            return

        result_langdetect = langdetect.detect(text)
        if result_langdetect == g.config["translate"]["target"]:
            # 母国語と同じ
            await talk_voice_with_nickname(nickname, text, cid)
            return

        translated_text = await translate(text, g.config["translate"]["target"])
        if translated_text == text:
            # 翻訳前後が一致
            await talk_voice_with_nickname(nickname, text, cid)
            return

        if not translated_text:
            translated_text = text

        await talk_voice_with_nickname(nickname, translated_text, cid)
        await self.bot.send_message(f"{translated_text} [by {user}]")


async def setup_database(
    db: asqlite.Pool,
) -> tuple[list[tuple[str, str]], list[eventsub.SubscriptionPayload]]:
    # Create our token table, if it doesn't exist..
    # You should add the created files to .gitignore or potentially store them somewhere safer
    # This is just for example purposes...

    query = """CREATE TABLE IF NOT EXISTS tokens(user_id TEXT PRIMARY KEY, token TEXT NOT NULL, refresh TEXT NOT NULL)"""
    async with db.acquire() as connection:
        await connection.execute(query)

        # Fetch any existing tokens...
        rows: list[sqlite3.Row] = await connection.fetchall("""SELECT * from tokens""")

        tokens: list[tuple[str, str]] = []
        subs: list[eventsub.SubscriptionPayload] = []

        bot_id = g.config["twitch"]["bot"]["id"]

        for row in rows:
            tokens.append((row["token"], row["refresh"]))

            # BOT自身のアカウントにはイベント購読を設定しない
            if row["user_id"] == bot_id:
                continue

            # 自分の配信チャンネル（row["user_id"]）のチャット・通知イベントを購読対象に追加
            subs.extend(
                [
                    eventsub.ChatMessageSubscription(
                        broadcaster_user_id=row["user_id"], user_id=bot_id
                    ),
                    eventsub.ChatNotificationSubscription(
                        broadcaster_user_id=row["user_id"], user_id=bot_id
                    ),
                ]
            )

    return tokens, subs
