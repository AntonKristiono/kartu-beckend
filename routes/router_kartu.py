from bson.objectid import ObjectId
from config.config import DB, CONF
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
import logging
import random
import string


from .model_kartu import KartuBase, KartuOnDb

router_kartu = APIRouter()


def validate_object_id(id_: str):
    try:
        _id = ObjectId(id_)
    except Exception:
        if CONF["fastapi"].get("debug", False):
            logging.warning("Invalid Object ID")
        raise HTTPException(status_code=400)
    return _id


async def _get_kartu_or_404(id_: str):
    _id = validate_object_id(id_)
    kartu = await DB.tbl_kartu.find_one({"_id": _id})
    if kartu:
        return fix_kartu_id(kartu)
    else:
        raise HTTPException(status_code=404, detail="Kartu not found")


def fix_kartu_id(kartu):
    kartu["id_"] = str(kartu["_id"])
    return kartu


def randomString(stringLength=6):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

# =================================================================================


@router_kartu.post("/post/", response_model=KartuOnDb)
async def add_kartu(kartu: KartuBase):
    kartu.createDate = datetime.utcnow()
    kartu.updateDate = datetime.utcnow()
    kartu.nama = kartu.nama.upper()
    print(kartu.dict())
    kartu_op = await DB.tbl_kartu.insert_one(kartu.dict())
    if kartu_op.inserted_id:
        kartu = await _get_kartu_or_404(kartu_op.inserted_id)
        kartu["id_"] = str(kartu["_id"])
        return kartu


@router_kartu.get("/getAll/", response_model=List[KartuOnDb])
async def get_all_kartus(limit: int = 10, skip: int = 0):
    kartus_cursor = DB.tbl_kartu.find().skip(skip).limit(limit)
    kartus = await kartus_cursor.to_list(length=limit)
    return list(map(fix_kartu_id, kartus))


@router_kartu.get("/{id_}", response_model=KartuOnDb)
async def get_kartu_by_id(id_: ObjectId = Depends(validate_object_id)):
    kartu = await DB.tbl_kartu.find_one({"_id": id_})
    if kartu:
        kartu["id_"] = str(kartu["_id"])
        return kartu
    else:
        raise HTTPException(status_code=404, detail="Kartu not found")

@router_kartu.delete("/{id_}", response_model=dict)
async def delete_kartu_by_id(id_: str):
    kartu_op = await DB.tbl_kartu.delete_one({"_id": ObjectId(id_)})
    if kartu_op.deleted_count:
        return {"status": f"deleted count: {kartu_op.deleted_count}"}


@router_kartu.put("/{id_}", response_model=KartuOnDb)
async def update_kartu(id_: str, kartu_data: KartuBase):
    kartu = await DB.tbl_kartu.find_one({"_id": ObjectId(id_)})
    if kartu:
        kartu_op = await DB.tbl_kartu.update_one(
            {"_id": ObjectId(id_)}, {"$set": kartu_data.dict()}
        )
        if kartu_op.modified_count:
            return await _get_kartu_or_404(id_)
        else:
            raise HTTPException(status_code=304)
    else:
        raise HTTPException(status_code=304)
