from typing import Optional
from enum import StrEnum
from dataclasses import dataclass
from datetime import datetime, date


__all__ = [
    'EmployeeContractType',
    'EmployeeContract'
]


class EmployeeContractType(StrEnum):
    permanent = 'Бессрочный'
    temporary = 'Срочный'
    civil_law = 'ГПХ'


@dataclass
class EmployeeContract:
    WorkerID: str
    SNILS: str
    WorkerName: str
    Department: str
    Position: str
    ContractType: EmployeeContractType
    DateStart: Optional[date] = None
    DateEnd: Optional[date] = None

    def __post_init__(self) -> None:
        self.ContractType = EmployeeContractType(self.ContractType)
        self.Position = self.Position.capitalize()
        
        if isinstance(self.DateStart, str):
            try:
                self.DateStart = datetime.strptime(self.DateStart, '%d.%m.%Y').date()
            except ValueError:
                self.DateStart = None

        if isinstance(self.DateEnd, str):
            try:
                self.DateEnd = datetime.strptime(self.DateEnd, '%d.%m.%Y').date()
            except ValueError:
                self.DateEnd = None
