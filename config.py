import sys
import inspect
from dataclasses import dataclass
from dotenv import dotenv_values


__all__ = [
    'PyrusConfig',
    'ZKGUConfig',
    'YandexCloudConfig',
    'AppConfig'
]


@dataclass(frozen=True, kw_only=True, repr=False)
class BaseConfig:
    pass


@dataclass(frozen=True, kw_only=True, repr=False)
class PyrusConfig(BaseConfig):
    PYRUS_AUTH_ENDPOINT: str
    PYRUS_PERSON_ID: str
    PYRUS_LOGIN: str
    PYRUS_SECRET_KEY: str
    PYRUS_HR_ROLE_ID: int
    PYRUS_HR_STEP: int


@dataclass(frozen=True, kw_only=True, repr=False)
class ZKGUConfig(BaseConfig):
    ZKGU_HOST: str
    ZKGU_BASE_PATH: str
    ZKGU_USER: str
    ZKGU_PASSWORD: str


@dataclass(frozen=True, kw_only=True, repr=False)
class YandexCloudConfig(BaseConfig):
    YANDEX_CLOUD_SQS_HOST: str
    YANDEX_CLOUD_PYRUS_ZKGU_QUEUE_NAME: str
    YANDEX_CLOUD_PYRUS_ZKGU_QUEUE_URL: str
    YANDEX_CLOUD_ACCESS_KEY_ID: str
    YANDEX_CLOUD_SECRET_ACCESS_KEY: str


@dataclass(frozen=True, kw_only=True, repr=False)
class AppConfig:
    pyrus: PyrusConfig
    zkgu: ZKGUConfig
    yandex_cloud: YandexCloudConfig

    @classmethod
    def from_env(cls, **kwargs) -> 'AppConfig':
        env_dir = getattr(sys, '_MEIPASS', '.')
        env = dotenv_values(env_dir + '/.env')

        data = {}

        for param in inspect.signature(cls).parameters.values():
            if isinstance(param.annotation, type(BaseConfig)):
                subconfig_cls = param.annotation
                subconfig_data = {}

                for subconfig_param in inspect.signature(param.annotation).parameters.values():
                    subconfig_param_value = env.get(subconfig_param.name, None)
                    
                    if subconfig_param_value is not None:
                        if subconfig_param_value.isdigit():
                            subconfig_param_value = int(subconfig_param_value)
                        
                        subconfig_data[subconfig_param.name] = subconfig_param_value
                    
                data[param.name] = subconfig_cls(**subconfig_data)
        
        return AppConfig(**data, **kwargs)
