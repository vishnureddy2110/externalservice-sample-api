from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class Address(BaseModel):
    model_config = ConfigDict(extra="ignore")
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = "US"


class Device(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_agent: Optional[str] = None
    device_id: Optional[str] = None
    session_id: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None


class Card(BaseModel):
    model_config = ConfigDict(extra="ignore")
    bin: Optional[str] = Field(default=None, min_length=6, max_length=8)
    last4: Optional[str] = Field(default=None, min_length=4, max_length=4)
    network: Optional[str] = None
    expiry_month: Optional[int] = Field(default=None, ge=1, le=12)
    expiry_year: Optional[int] = Field(default=None, ge=2020, le=2100)


class Payment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    amount: Optional[float] = None
    currency: Optional[str] = "USD"
    card: Optional[Card] = None


class RequestData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    first_name: str
    last_name: str
    email: EmailStr
    ip: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None

    billing_address: Optional[Address] = None
    shipping_address: Optional[Address] = None
    device: Optional[Device] = None


class EnrichRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    request_id: str
    transaction_id: str
    transaction_time: datetime
    data: RequestData
    payment: Optional[Payment] = None

    customer_id: Optional[int] = None
    merchant_id: Optional[str] = None
    channel: Optional[str] = None
