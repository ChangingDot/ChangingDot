class SimpleClass:
    def __init__(self, value: str):
        self.attribute = value

    def method(self) -> str:
        return f"The value of attribute is: {self.attribute}"
