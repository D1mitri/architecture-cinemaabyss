from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from fastapi import status

class MovieEvent(BaseModel):
    movie_id: int = Field(..., description="Идентификатор фильма", example=1)
    title: str = Field(..., description="Название фильма", example="Inception")
    action: str = Field(..., description="Действие с фильмом", example="viewed")
    user_id: Optional[int] = Field(None, description="Идентификатор пользователя", example=1)
    rating: Optional[float] = Field(None, description="Рейтинг", example=8.5)
    genres: Optional[List[str]] = Field(None, description="Жанры фильма", example=["Sci-Fi", "Action"])
    description: Optional[str] = Field(None, description="Описание фильма", example="A mind-bending thriller")

class UserInput(BaseModel):
    username: str = Field(..., description="Имя пользователя", example="Username")

class PaymentInput(BaseModel):
    user_id: int = Field(..., description="Идентификатор пользователя", example=1)
    amount: float = Field(..., description="Сумма платежа", example=8.88)

class EventResponse(BaseModel):
    event_id: str
    status: str
    timestamp: datetime

class SuccessResponse(BaseModel):
    status_code: int = Field(
        default=status.HTTP_201_CREATED,
        example=status.HTTP_201_CREATED,
        description="HTTP status code"
    )
    detail: str = Field(
        default="Resource created successfully",
        example="Resource created successfully"
    )

class Error(BaseModel):
    detail: str
    code: int