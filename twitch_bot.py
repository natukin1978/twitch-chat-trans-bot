import logging
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
from voice_map_helper import get_cid

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
        await self.add_token(payload.access_token, payload.refresh_token)

        if not payload.user_id:
            return

        if payload.user_id == self.bot_id:
            # We usually don't want subscribe to events on the bots channel...
            return

        # A list of subscriptions we would like to make to the newly authorized channel...
        subs: list[eventsub.SubscriptionPayload] = [
            eventsub.ChatMessageSubscription(
                broadcaster_user_id=payload.user_id, user_id=self.bot_id
            ),
        ]

        resp: twitchio.MultiSubscribePayload = await self.multi_subscribe(subs)
        if resp.errors:
            logger.warning(
                "Failed to subscribe to: %r, for user: %s", resp.errors, payload.user_id
            )

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
        logger.info("Successfully logged in as: %s", self.bot_id)
        owner_user = await self.get_owner_user()
        g.owner_attr = {
            "id": owner_user.id,
            "name": owner_user.name,
            "display_name": owner_user.display_name,
            "description": owner_user.description,
        }

    def get_owner_partial_user(self) -> twitchio.PartialUser:
        return self.create_partialuser(user_id=self.owner_id)

    async def get_owner_user(self) -> twitchio.User:
        return await self.fetch_user(id=self.owner_id)

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
        if payload.chatter.id == self.bot.bot_id:
            return

        # fragmentsを使ってテキスト部分だけを繋ぎ合わせる
        # fragment.type が "text" のものだけを取り出す
        text = "".join(
            fragment.text for fragment in payload.fragments if fragment.type == "text"
        )

        # 前後の余計な空白を整える
        text = text.strip()
        if not text:
            return

        user = payload.chatter.display_name
        cid = get_cid(user)
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

        # if is_cmd:
        #     # コマンドなら翻訳しない
        #     # 読み上げない
        #     return

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

            if row["user_id"] == bot_id:
                continue

            subs.extend(
                [
                    eventsub.ChatMessageSubscription(
                        broadcaster_user_id=row["user_id"], user_id=bot_id
                    )
                ]
            )

    return tokens, subs
