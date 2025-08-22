from typing import Optional
from requests import request, Response

from common.utils import json_dump
from config import PyrusConfig

from .types import PyrusApprovalChoices
from .exceptions import PyrusException


__all__ = [
    'PyrusService',
    'PyrusApprovalChoices'
]


class PyrusService:
    """
    Класс для работы с `Pyrus`
    """

    __name__ = 'PyrusService'

    def __init__(self, config: PyrusConfig) -> None:
        self.config = config

        self.api_url: str = ''
        self.files_url: str = ''
        self._access_token: Optional[str] = None
    
    def auth(self) -> bool:
        """
        Метод для авторизации в `Pyrus`

        Returns:
            bool: True - в случае успешной авторизации, False в случае, \
            если авторизация завершилась с ошибкой
        """
        
        auth_response = request(
            'POST',
            self.config.PYRUS_AUTH_ENDPOINT,
            data=json_dump({
                'login': self.config.PYRUS_LOGIN,
                'security_key': self.config.PYRUS_SECRET_KEY,
                'person_id': self.config.PYRUS_PERSON_ID
            }),
            headers={
                'Content-Type': 'application/json'
            }
        )

        if auth_response.ok:
            auth_response_data = auth_response.json()

            self.api_url = auth_response_data.get('api_url')
            self.files_url = auth_response_data.get('files_url')
            self._access_token = auth_response_data.get('access_token')

            return True
        else:
            raise PyrusException(f'[{self.__name__}] Авторизация не удалась. Код ответа: {auth_response.status_code}')

    def comment_task(
        self,
        task_id: int | str,
        text: str,
        approval_choice: Optional[PyrusApprovalChoices] = 'acknowledged',
        approvals_added: Optional[list[list[dict]]] = [],
        approvals_removed: Optional[list[list[dict[str, int | str]]]] = []
    ) -> None:
        """
        Метод для комментирования задачи в `Pyrus`

        Args:
            task_id (int | str): Номер задачи в `Pyrus`
            text (str): Текст сообщения
            approval_choice (PyrusApprovalChoices, optional): Статус согласования этапа

        Returns:
            None
        """

        if self._access_token is None:
            self.auth()

        comment_task_response = request(
            'POST',
            self.api_url + f'tasks/{task_id}/comments',
            data=json_dump({
                'formatted_text': text,
                'approval_choice': approval_choice,
                'approvals_added': approvals_added,
                'approvals_removed': approvals_removed
            }),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self._access_token}'
            }
        )

        if not comment_task_response.ok:
            raise PyrusException((
                f'[{self.__name__}] Не удалось добавить комментарий к задаче, ',
                f'ответ: {comment_task_response.status_code} {comment_task_response.text}'
            ))
