from bson import ObjectId
from config.config import DB, CONF
from fastapi import APIRouter, Depends, HTTPException, Response, File, UploadFile
from typing import List
from datetime import datetime, date, timedelta
import pandas as pd
import logging
import random
import string
from io import BytesIO

from .model_kartu import KartuBase, KartuOnDb

router_bulkDataKartu = APIRouter()

def validate_object_id(id_: str):
    try:
        _id = ObjectId(id_)
    except Exception:
        if CONF["fastapi"].get("debug",False):
            logging.warning("Invalid Object ID")
        raise HTTPException (status_code=400)
    return _id

async def _get_dataKartu_or_404(id_: str):
    _id = validate_object_id(id_)
    dataKartu = await DB.tbl_dataKartu.find_one({"_id": _id})
    if dataKartu:
        return fix_id(dataKartu)
    else:
        raise HTTPException(status_code=404, detail="dataKartu not found")

def fix_id(dataKartu):
    dataKartu["id_"] = str(dataKartu["_id"])
    return dataKartu

def randomString(stringLength=6):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

@router_bulkDataKartu.post("/upload_bulkData") #upload data didalam kartu dari excel
async def upload_bulkData(file: UploadFile = File(...)):
    bd = pd.read_excel(file.file)
    print(bd)
    result = []
    kartu = KartuBase()
    for index, row in bd.iterrows():
        kartu.createDate = datetime.utcnow ()
        kartu.updateDate = datetime.utcnow ()
        kartu.companyId = row["Nama Sekolah"].upper()
        kartu.accountId = row["NIS"]
        kartu.nama = row["Nama"]
        kartu.tempatLahir = row["Tempat Lahir"]
        kartu.tanggalLahir = row["Tanggal Lahir"]
        kartu.images = row["Image"]
        kartu.alamat = row["Alamat"]
        result.append(kartu.dict())
    print(result)
    DB.tbl_dataKartu.insert_many(result)
    return {"ok"}
