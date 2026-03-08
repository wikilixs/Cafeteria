from pathlib import Path


from pydantic_settings import BaseSettings, SettingsConfigDict





BASE_DIR = Path(__file__).resolve().parent.parent  # carpeta raíz (donde está main.py)





class Configuracion(BaseSettings):


    host: str


    port: int


    user: str


    password: str


    database: str


    secret_key: str = "cafeteria_secret_key_2026"





    model_config = SettingsConfigDict(


        env_file=BASE_DIR / ".env",


        env_file_encoding="utf-8",


        case_sensitive=False,


    )





settings = Configuracion()