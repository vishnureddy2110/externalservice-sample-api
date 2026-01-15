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


# Simplified models for individual service APIs
class ServiceRequestData(BaseModel):
    """Simplified data model for individual service APIs"""
    model_config = ConfigDict(extra="ignore")
    first_name: str
    last_name: str
    email: EmailStr
    ip: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None


class EkataRequest(BaseModel):
    """Request model for Ekata API"""
    model_config = ConfigDict(extra="ignore")
    request_id: str
    data: ServiceRequestData


class EmailageRequest(BaseModel):
    """Request model for Emailage API"""
    model_config = ConfigDict(extra="ignore")
    request_id: str
    data: ServiceRequestData


# Response models
class EkataResponseData(BaseModel):
    """Response data echoing back request info"""
    model_config = ConfigDict(extra="ignore")
    fname: str
    l_name: str
    email: EmailStr
    ip: Optional[str] = None
    homephone: Optional[str] = None
    workphone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None


class EkataPayload(BaseModel):
    """Ekata risk assessment payload"""
    model_config = ConfigDict(extra="ignore")
    risk_score: int
    first_name_match: bool
    last_name_match: bool
    email_risk: int
    ip_risk: int
    phone_risk: int


class EkataResponse(BaseModel):
    """Response model for Ekata API"""
    model_config = ConfigDict(extra="ignore")
    request_id: str
    data: EkataResponseData
    ekata_payload: EkataPayload


class EmailagePayload(BaseModel):
    """Emailage enrichment payload"""
    model_config = ConfigDict(extra="ignore")
    score: int
    email_first_seen: str
    email_last_seen: str
    domain_exists: bool
    disposable: bool
    free_provider: bool


class EmailageResponse(BaseModel):
    """Response model for Emailage API"""
    model_config = ConfigDict(extra="ignore")
    request_id: str
    data: ServiceRequestData
    emailage_payload: EmailagePayload
