
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator
)


# Common username validation
Username = Annotated[
    str,
    StringConstraints(
        strict=True,
        min_length=3,
        max_length=50,
        pattern=r"^[A-Za-z0-9_.-]+$"
    )
]


class StrictRequest(BaseModel):
    # Reject unexpected fields such as role="admin"
    model_config = ConfigDict(extra="forbid")


class RegisterRequest(StrictRequest):
    username: Username

    password: Annotated[
        str,
        StringConstraints(
            strict=True,
            min_length=8,
            max_length=128
        )
    ]


class LoginRequest(StrictRequest):
    username: Username

    password: Annotated[
        str,
        StringConstraints(
            strict=True,
            min_length=1,
            max_length=128
        )
    ]


class RecordCreateRequest(StrictRequest):
    title: Annotated[
        str,
        StringConstraints(
            strict=True,
            min_length=1,
            max_length=100
        )
    ]

    body: Annotated[
        str,
        StringConstraints(
            strict=True,
            min_length=1,
            max_length=10000
        )
    ]

    @field_validator("title")
    @classmethod
    def validate_title(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Title cannot contain only spaces")

        return value

    @field_validator("body")
    @classmethod
    def validate_body(cls, value):
        if not value.strip():
            raise ValueError("Body cannot contain only spaces")

        return value
