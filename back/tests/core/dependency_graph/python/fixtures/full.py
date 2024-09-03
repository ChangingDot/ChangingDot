import datetime
import logging

logging.basicConfig(level=logging.INFO)


class GenericClass:
    def __init__(
        self, name: str, value: int, created_at: datetime.datetime | None = None
    ):
        self.name = name
        self.value = value
        self.created_at = created_at if created_at else datetime.datetime.now()
        logging.info(f"GenericClass created: {self}")

    def __repr__(self) -> str:
        return f"GenericClass(name={self.name}, value={self.value}, created_at={self.created_at})"

    def update_value(self, new_value: int) -> None:
        logging.info(f"Updating value from {self.value} to {new_value}")
        self.value = new_value

    def save_to_file(self, file_path: str) -> None:
        try:
            with open(file_path, "w") as file:
                file.write(str(self))
            logging.info(f"Object saved to file: {file_path}")
        except Exception as e:
            logging.error(f"Failed to save object to file: {e}")

    def load_from_file(cls, file_path: str) -> None:
        try:
            with open(file_path) as file:
                data = file.read()
            name, value, created_at = data.strip().split(", ")
            name = name.split("=")[1]
            return None
        except Exception as e:
            logging.error(f"Failed to load object from file: {e}")
            return None
