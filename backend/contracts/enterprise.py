from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Organization(BaseModel):
    id: str
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class User(BaseModel):
    id: str
    organization_id: str
    email: str
    password_hash: str
    role_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Team(BaseModel):
    id: str
    organization_id: str
    name: str
    department_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Department(BaseModel):
    id: str
    organization_id: str
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AuditLog(BaseModel):
    id: Optional[str] = None
    organization_id: str
    actor: str
    action: str
    resource: str
    resource_id: str
    details: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Role(BaseModel):
    id: str
    organization_id: str
    name: str
    permissions: List[str] = Field(default_factory=list)

class ApiKey(BaseModel):
    id: str
    organization_id: str
    key_hash: str
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
