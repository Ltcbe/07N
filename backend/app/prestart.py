from loguru import logger

from .database import Base, engine


def init_db() -> None:
    logger.info("Creating database tables if they do not exist")
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
