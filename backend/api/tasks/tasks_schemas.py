from pydantic import BaseModel


class TaskSchema(BaseModel):
    user_id: int
    is_regular_remind: bool = False
    description: str
