import configparser
import os
from dataclasses import dataclass
from typing import List, Callable

from cores.log import LOG


@dataclass
class AppConfig:
    project_name: str = "My FastAPI Project"
    api_version: str = "/api/v1"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000


@dataclass
class MySQLConfig:
    host: str
    port: int
    user: str
    password: str
    database: str

    @property
    def db_url(self):
        return f"mysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    @property
    def db_url_pymysql(self):
        return f'mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}'


@dataclass
class RedisConfig:
    host: str
    port: int
    password: str
    default_db: int

    @property
    def db_url(self):
        return f"redis://:{self.password}@{self.host}:{self.port}/{self.default_db}"


@dataclass
class SecurityConfig:
    secret_key: str
    algorithm: str
    token_expire_days: int


@dataclass
class Settings:
    app: AppConfig
    mysql: MySQLConfig
    redis: RedisConfig
    security: SecurityConfig


def get_config_path() -> str:
    """获取配置文件的路径，确保路径为绝对路径"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.getenv("CONFIG_FILE_PATH", "../config.ini")
    if not os.path.isabs(config_file_path):
        config_file_path = os.path.abspath(os.path.join(base_dir, config_file_path))
    return config_file_path


def parse_config_list(config, section, key, value_type: Callable[[str], object] = str, default=None) -> List[object]:
    """
    解析配置为指定类型的列表

    :param config: 配置对象
    :param section: 配置部分
    :param key: 配置项的键
    :param value_type: 列表元素的目标类型（如 int, str, float）
    :param default: 配置解析失败时的默认值
    :return: 转换后的列表或默认值
    """
    try:
        # 根据传入的类型转换配置项的值
        return [value_type(x) for x in config.get(section, key).split(",")]
    except (ValueError, AttributeError, KeyError) as e:
        LOG.error(f"解析配置 {section}.{key} 时出错: {e}")
        return default or []  # 如果出错则返回默认值（默认为空列表）


def read_config() -> Settings:
    """读取配置文件并返回配置设置"""
    file_path = get_config_path()

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    config = configparser.ConfigParser()
    config.read(file_path)

    app_config = AppConfig(**config["app"])
    app_config.debug = config.getboolean("app", "debug")
    app_config.port = config.getint("app", "port")

    mysql_config = MySQLConfig(**config["mysql"])
    redis_config = RedisConfig(**config["redis"])
    security_config = SecurityConfig(**config["security"])
    security_config.token_expire_days = config.getint("security", "token_expire_days")

    return Settings(
        app=app_config,
        mysql=mysql_config,
        redis=redis_config,
        security=security_config,
    )


settings = read_config()
