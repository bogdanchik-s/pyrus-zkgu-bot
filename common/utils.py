import json
from typing import Any


def json_dump(obj: Any) -> str:
    """
    Функция для преобразования объекта в строку JSON формата

    Args:
        obj (Any): Объект для преобразования

    Returns:
        str: Строка JSON формата
    """
    
    return json.dumps(
        obj,
        ensure_ascii=False
    )
