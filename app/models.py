from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BookIn(BaseModel):
    """What the client sends: a book without id."""

    model_config = ConfigDict(strict=True)

    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    year: int | None = Field(default=None, ge=0)
    read: bool = False

    @field_validator("year")
    @classmethod
    def year_not_in_future(cls, value: int | None) -> int | None:
        if value is not None and value > date.today().year:
            raise ValueError("year must not be after the current year")
        return value


class Book(BookIn):
    """What the API sends back: a book with its id."""

    id: int
