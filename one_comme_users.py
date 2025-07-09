import global_value as g
from csv_helper import read_csv_to_list
from dict_helper import get_first_non_none_value


class OneCommeUsers:
    @staticmethod
    def read_one_comme_users():
        pathUsersCsv = g.config["oneComme"]["pathUsersCsv"]
        if not pathUsersCsv:
            return None

        return read_csv_to_list(pathUsersCsv)

    @staticmethod
    def get_nickname(displayName: str) -> str:
        one_comme_users = OneCommeUsers.read_one_comme_users()

        filtered_rows = list(filter(lambda row: row[1] == displayName, one_comme_users))
        for filtered_row in filtered_rows:
            nickname = filtered_row[4]
            if nickname:
                return nickname

        return None

    @staticmethod
    def update_nickname(json_data: dict[str, any]) -> None:
        nickname = OneCommeUsers.get_nickname(json_data["displayName"])
        if not nickname:
            nickname = get_first_non_none_value(json_data, ["displayName", "id"])

        json_data["nickname"] = nickname

    @staticmethod
    def update_is_first_on_stream(json_data: dict[str, any]) -> None:
        name = json_data["id"]
        val = None
        if name not in g.map_is_first_on_stream:
            val = True
        else:
            val = g.map_is_first_on_stream[name]
        json_data["isFirstOnStream"] = val
        g.map_is_first_on_stream[name] = False
        OneCommeUsers.save_is_first_on_stream()

    @staticmethod
    def update_message_json(json_data: dict[str, any]) -> None:
        OneCommeUsers.update_is_first_on_stream(json_data)
        OneCommeUsers.update_nickname(json_data)
