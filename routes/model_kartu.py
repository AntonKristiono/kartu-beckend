# from enum import Enum
from pydantic import BaseModel
# from typing import List, Optional
from datetime import datetime


class KartuBase(BaseModel):
    createDate: datetime = None
    updateDate: datetime = None
    companyId: str = None
    accountId: str  # nis nomor_akun dll
    nama: str
    tempatLahir: str = None
    tanggalLahir: str = None
    images: str = None


class KartuOnDb(KartuBase):
    id_: str
