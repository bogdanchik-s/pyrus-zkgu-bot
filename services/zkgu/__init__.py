from urllib.parse import quote
from requests.sessions import Session
from requests.exceptions import RequestException

from config import ZKGUConfig

from .types import EmployeeContractType, EmployeeContract
from .exceptions import ZKGUException


__all__ = [
    'ZKGUService',
    'EmployeeContractType',
    'EmployeeContract'
]


class ZKGUService:
    """
    Класс для работы с 1С:ЗКГУ    
    """

    __name__ = 'ZKGUService'

    def __init__(self, config: ZKGUConfig) -> None:
        self._config = config

        self._session = Session()
        self._session.auth = (self._config.ZKGU_USER, self._config.ZKGU_PASSWORD)
    
    def get_employee_contracts(self, worker_name: str, worker_snils: str) -> list[EmployeeContract]:
        print(f'[{self.__name__}] Получение данных о наличии у {worker_name} трудовых отношений с Академией...')
        
        employee_contracts: list[EmployeeContract] = []
        
        url = self._config.ZKGU_HOST + self._config.ZKGU_BASE_PATH + '/EmployeeContracts'
        params = quote(f'Name={worker_name}&SNILS={worker_snils}', safe='/=&')

        try:
            response = self._session.get(f'{url}?{params}')
        except Exception as e:
            raise ZKGUException((
                f'[{self.__name__}] Произошла ошибка при отправки запроса: {e.__class__.__name__}.'
            ))

        if response.ok:
            response_data = response.json()
                    
            if isinstance(response_data, list):
                for employee_contract in response_data:
                    employee_contracts.append(EmployeeContract(**employee_contract))
            else:
                raise ZKGUException(f'[{self.__name__}] Неизвестный тип ответа от сервиса.')
        else:
            raise ZKGUException((
                f'[{self.__name__}] Произошла ошибка при выполнении запроса, '
                f'ответ: {response.status_code} {response.text}'
            ))

        print(f'[{self.__name__}] Найдено договоров c {worker_name}: {len(employee_contracts)}.')

        return employee_contracts
