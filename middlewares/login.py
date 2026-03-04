import logging
import sys
from datetime import datetime


def setup_logging():
    # Formato de los logs
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Handler archivo
    file_handler = logging.FileHandler(
        f"logs/app_{datetime.now().strftime('%Y-%m-%d')}.log",
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # Logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Silenciar librerías muy verbosas
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("psycopg2").setLevel(logging.WARNING)