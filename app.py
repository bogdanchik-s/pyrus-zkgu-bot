import time
import json
from datetime import datetime

from common.types import Person
from services.pyrus import PyrusService
from services.zkgu import ZKGUService, EmployeeContractType
from services.yandex_cloud import YandexCloudService, MessageGroup

from config import AppConfig


INTERVAL = 60 * 5
DATE_FORMAT = '%d.%m.%Y'


class App:
    """
    Главный класс приложения
    """

    __name__ = 'App'

    def __init__(self, config: AppConfig) -> None:
        self._config = config

        self._pyrus_service = PyrusService(config=self._config.pyrus)
        self._zkgu_service = ZKGUService(config=self._config.zkgu)
        self._yandex_cloud_service = YandexCloudService(config=self._config.yandex_cloud)

    def start_app(self) -> None:
        print(f'[{self.__name__}] Успешно запущено.')

        while True:
            try:
                self._yandex_cloud_service.handle_messages_groups(self._process)
                self._sleep()
            except (KeyboardInterrupt, SystemExit):
                break

    def _process(self, message_group: MessageGroup) -> bool:
        task_id = message_group.group_id
        
        print(f'[{self.__name__}] Обработка задачи в Pyrus #{task_id}...')

        # Последнее сообщение из группы берется намеренно,
        # так как может содержать более актуальные данные,
        # например, если в задаче были обновлены какие-то поля
        message = message_group.messages[-1]

        try:
            person = Person(**json.loads(message.text))
            person_contracts = self._zkgu_service.get_employee_contracts(
                worker_name=person.fullname,
                worker_snils=person.snils
            )

            if not person_contracts:
                self._pyrus_service.comment_task(
                    task_id=task_id,
                    text=f'{person.fullname} в трудовых отношениях с РАНХиГС (без филиалов) по состоянию на {datetime.now().strftime(DATE_FORMAT)} не состоит.<br><br><b>Примечание</b><br>Нет технической возможности проверить информацию о трудоустройстве в филиалах.',
                    approval_choice='approved'
                )

                return True

            person_contract = min(person_contracts, key=lambda pc: pc.DateStart if pc.DateStart is not None else False)

            match person_contract.ContractType:
                case EmployeeContractType.permanent:
                    self._pyrus_service.comment_task(
                        task_id=task_id,
                        text=(
                           f'{person.fullname} имеет бессрочные трудовые отношения с Академией '
                           f'с {person_contract.DateStart.strftime(DATE_FORMAT) if person_contract.DateStart is not None else "неизвестной даты"} '
                           f'в подразделении «{person_contract.Department}» на должности «{person_contract.Position}».'
                        ),
                        approval_choice='rejected'
                    )
                
                case EmployeeContractType.temporary:
                    self._pyrus_service.comment_task(
                        task_id=task_id,
                        text=(
                           f'{person.fullname} имеет срочные трудовые отношения с Академией '
                           f'с {person_contract.DateStart.strftime(DATE_FORMAT) if person_contract.DateStart is not None else "неизвестной даты"} '
                           f'по {person_contract.DateEnd.strftime(DATE_FORMAT) if person_contract.DateEnd is not None else "неизвестную дату"} '
                           f'в подразделении «{person_contract.Department}» на должности «{person_contract.Position}».'
                        ),
                        approval_choice='rejected'
                    )
                
                case EmployeeContractType.civil_law:
                    self._pyrus_service.comment_task(
                        task_id=task_id,
                        text=(
                           f'{person.fullname} имеет договор ГПХ с Академией '
                           f'с {person_contract.DateStart.strftime(DATE_FORMAT) if person_contract.DateStart is not None else "неизвестной даты"} '
                           f'по {person_contract.DateEnd.strftime(DATE_FORMAT) if person_contract.DateEnd is not None else "неизвестную дату"}.'
                        ),
                        approval_choice='approved'
                    )
            
            print(f'[{self.__name__}] Обработка задачи в Pyrus #{task_id} завершена.')        

            return True
        except Exception as e:
            print(f'[{self.__name__}] В процесса обработки задачи в Pyrus #{task_id} произошла ошибка:')        
            print(e)
            
            self._pyrus_service.comment_task(
                task_id=task_id,
                text=(
                    f'<b>Ошибка: {e.__class__.__name__}</b><br>'
                    'В процессе обработки задачи произошла ошибка. '
                    'Обратитесь в <a href="https://help.ranepa.ru/portal">Техническую поддержку РАНХиГС</a>.'
                ),
                approval_choice='revoked',
                approvals_added=[*([] for _ in range(self._config.pyrus.PYRUS_HR_STEP-1)), [{'id': self._config.pyrus.PYRUS_HR_ROLE_ID}]]
            )

            return False
    
    def _sleep(self, seconds: int = INTERVAL) -> None:
        for left_time in range(seconds, -1, -1):
            left_min, left_sec = divmod(left_time, 60)
            print(f'\r[{self.__name__}] До окончания времени ожидания осталось {left_min:02}:{left_sec:02} сек.', end='')
            time.sleep(1)
        
        print()


if __name__ == '__main__':
    app = App(config=AppConfig.from_env())
    app.start_app()
