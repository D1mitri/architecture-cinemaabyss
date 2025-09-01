from datetime import datetime
import os
import uuid
import logging
from fastapi import FastAPI, Depends, HTTPException, status
from .producer import EventProducer, get_producer
from .models.schemas import MovieEvent, UserInput, PaymentInput, EventResponse, Error
from fastapi.responses import JSONResponse
from datetime import datetime
import json
from typing import Optional

app = FastAPI()
logging.basicConfig(level=logging.INFO)

@app.post("/api/events/movie",
          response_model=EventResponse,
          status_code=status.HTTP_201_CREATED,
          responses={
              422: {"description": "Validation Error"},
              500: {"model": Error}
          })
async def create_movie_event(
    event: MovieEvent,
    producer: EventProducer = Depends(get_producer)
):
    """Создание события movie"""
    try:
        event_id = str(uuid.uuid4())
        producer.produce_event(
            topic="movie_events",
            event_type=event.action,
            data=event.dict()
        )
        return EventResponse(
            event_id=event_id,
            status="success",
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/api/events/user",
          response_model=EventResponse,
          status_code=status.HTTP_201_CREATED,
          responses={
              422: {"description": "Validation Error"},
              500: {"model": Error}
          })
async def create_user_event(
    user: UserInput,
    producer: EventProducer = Depends(get_producer)
):
    """Создание события user"""
    try:
        event_id = str(uuid.uuid4())
        producer.produce_event(
            topic="user_events",
            event_type="user_created",
            data=user.dict()
        )
        return EventResponse(
            event_id=event_id,
            status="success",
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/api/events/payment",
          response_model=EventResponse,
          status_code=status.HTTP_201_CREATED,
          responses={
              422: {"description": "Validation Error"},
              500: {"model": Error}
          })
async def create_payment_event(
    payment: PaymentInput,
    producer: EventProducer = Depends(get_producer)
):
    """Создание события payment"""
    try:
        event_id = str(uuid.uuid4())
        producer.produce_event(
            topic="payment_events",
            event_type="payment_processed",
            data=payment.dict()
        )
        return EventResponse(
            event_id=event_id,
            status="success",
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/health")
async def health_check():
    return {"status": True}

@app.get("/api/events/health")
async def events_health_check():
    return {"status": True}