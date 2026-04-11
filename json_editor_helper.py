def sort_dict_by_schema(data, schema):
    """
    schema の properties に定義されている順序 (または propertyOrder) に従って
    data のキーを並び替える再帰関数
    """
    if not isinstance(data, dict) or "properties" not in schema:
        return data

    # スキーマからプロパティリストを取得
    props = schema.get("properties", {})

    # propertyOrder がある場合はそれでソート、なければ記述順
    sorted_keys = sorted(
        props.keys(),
        key=lambda k: props[k].get("propertyOrder", 999)
    )

    result = {}
    for key in sorted_keys:
        if key in data:
            val = data[key]
            # ネストされたオブジェクトがある場合は再帰的に処理
            if isinstance(val, dict) and "properties" in props[key]:
                result[key] = sort_dict_by_schema(val, props[key])
            else:
                result[key] = val

    # スキーマに定義されていないがデータには存在するキー（もしあれば）を末尾に追加
    for key in data:
        if key not in result:
            result[key] = data[key]

    return result
