# from enum import Enum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ImageBase(BaseModel):
    file_type: str = None
    name: str = None


class MediaBase(ImageBase):
    createTime: Optional[datetime] = None
    updateTime: Optional[datetime] = None
    companyId: str = None
    creatorId: str = None
    used: int = 0
    temp: bool = True
    origin_name: str = None
    file_name: str = None  # 20_05_20_100x100_abcdefgh_ico/thumb/std


class MediaBaseOnDb(MediaBase):
    _id: str
