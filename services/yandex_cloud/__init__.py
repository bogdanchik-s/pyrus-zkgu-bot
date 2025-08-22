import boto3
from collections.abc import Iterable

from config import YandexCloudConfig

from .types import MessageGroupId, Message, MessageGroup, MessagesGroupsHandler


__all__ = [
    'YandexCloudService',
    'MessageGroupId',
    'Message',
    'MessageGroup',
    'MessagesGroupsHandler'
]


class YandexCloudService:
    """
    Класс для работы с `Yandex Cloud`
    """

    __name__ = 'YandexCloudService'

    def __init__(self, config: YandexCloudConfig) -> None:
        self._config = config

        self._sqs_client = boto3.client(
            service_name='sqs',
            region_name='ru-central1',
            endpoint_url=self._config.YANDEX_CLOUD_SQS_HOST,
            aws_access_key_id=self._config.YANDEX_CLOUD_ACCESS_KEY_ID,
            aws_secret_access_key=self._config.YANDEX_CLOUD_SECRET_ACCESS_KEY
        )
    
    def handle_messages_groups(self, handler: MessagesGroupsHandler) -> None:
        """
        Метод для обработки сообщений
        """
        print(f'[{self.__name__}] Обработка сообщений...')

        messages_groups = self._receive_messages()

        for message_group in messages_groups:
            deleteMessages = handler(message_group)

            if deleteMessages:
                self._delete_messages([*message_group.messages])

        print(f'[{self.__name__}] Обработка сообщений завершена.')

    def _receive_messages(self) -> list[MessageGroup]:
        print(f'[{self.__name__}] Получение сообщений из очереди {self._config.YANDEX_CLOUD_PYRUS_ZKGU_QUEUE_NAME}...')
        
        messages_groups: dict[MessageGroupId, MessageGroup] = {}
        
        receive_message_response = self._sqs_client.receive_message(
            QueueUrl=self._config.YANDEX_CLOUD_PYRUS_ZKGU_QUEUE_URL,
            AttributeNames=['MessageGroupId'],
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20,
        )

        for receive_message in receive_message_response.get('Messages', []):
            message_group_id = receive_message.get('Attributes', {}).get('MessageGroupId', '')

            message = Message(
                text=receive_message.get('Body', ''),
                receipt_handle=receive_message.get('ReceiptHandle', '')
            )

            if message_group_id not in messages_groups:
                messages_groups[message_group_id] = MessageGroup(
                    group_id=message_group_id,
                    messages=[message]
                )
            else:
                messages_groups[message_group_id].messages.append(message)

        print(f'[{self.__name__}] Получено групп сообщений: {len(messages_groups)}.')

        return [*messages_groups.values()]

    def _delete_messages(self, messages: Iterable[Message]) -> None:
        print(f'[{self.__name__}] Удаление сообщений...')
        
        for message in messages:
            self._sqs_client.delete_message(
                QueueUrl=self._config.YANDEX_CLOUD_PYRUS_ZKGU_QUEUE_URL,
                ReceiptHandle=message.receipt_handle
            )

        print(f'[{self.__name__}] Удаление сообщений завершено.')
