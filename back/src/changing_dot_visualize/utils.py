from typing import Any

from pydantic import BaseModel


def convert_to_dict(
    input_data: BaseModel | dict[Any, Any] | list[Any],
) -> Any:
    if isinstance(input_data, BaseModel):
        # Convert Pydantic BaseModel to dictionary
        return {k: convert_to_dict(v) for k, v in input_data.model_dump().items()}
    elif isinstance(input_data, dict):
        # Recursively convert dictionary values
        return {k: convert_to_dict(v) for k, v in input_data.items()}
    elif isinstance(input_data, list):
        # Recursively convert list elements
        return [convert_to_dict(item) for item in input_data]
    else:
        # Return the data as-is if it's a basic type
        return input_data


def get_items(data: dict[Any, Any] | BaseModel) -> list[tuple[str, Any]]:
    if isinstance(data, BaseModel):
        data_dict = data.model_dump()
    elif isinstance(data, dict):
        data_dict = data

    return list(data_dict.items())
