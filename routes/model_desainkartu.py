#!/usr/bin/env python3
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CardBase(BaseModel):
    file_type: str = None
    name: str = None

class MediaCardBase(CardBase):
    createTime: Optional[datetime] = None
    updateTime: Optional[datetime] = None
    companyId: str = None
    creatorId: str = None
    used: int = 0
    temp: bool = True
    origin_name: str = None
    file_name: str = None

class MediaCardBaseOnDb(MediaCardBase):
    _id: str
    companyName: str
