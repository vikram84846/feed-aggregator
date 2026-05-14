from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class SubscriptionSchema(BaseModel):
    topic_name: str = Field(min_length=2, max_length=100)

    model_config = ConfigDict(str_strip_whitespace=True, str_to_lower=True)


class SubscriptionResponseSchema(BaseModel):
    id: str
    user_id: str
    topic_id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserTopicsResponse(BaseModel):
    topics: list[str]
