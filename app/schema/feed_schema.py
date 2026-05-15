from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime

class PostResponse(BaseModel):
    id: str
    title: str
    content: str
    published_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FeedQueryParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10)
    search: str | None = Field(default=None, min_length=2, max_length=100)
    topic_name: str | None = Field(default=None, min_length=2, max_length=50)
    source_name: str | None = Field(default=None, min_length=2, max_length=50)
    model_config = ConfigDict(str_strip_whitespace=True, str_to_lower=True)

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, value):
        if value <= 0:
            raise ValueError("limit should be greater than 0")
        return min(value, 100)
