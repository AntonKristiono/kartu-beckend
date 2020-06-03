# from enum import Enum
from pydantic import BaseModel
# from typing import List, Optional
from datetime import datetime


class KartuBase(BaseModel):
    createDate: datetime = None
    updateDate: datetime = None
    companyId: str = None
    accountId: str = None # nis nomor_akun dll
    nama: str = None
    tempatLahir: str = None
    tanggalLahir: str = None
    images: str = None
    alamat: str = None


class KartuOnDb(KartuBase):
    id_: str
