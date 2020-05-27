from bson.objectid import ObjectId
from config.config import DB, CONF
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List
from datetime import datetime, date
import logging
import random
import string
import shutil
import os
import cv2
from PIL import Image

from .model_desainkartu import MediaCardBase

router_desainkartu = APIRouter()

def validate_object_id(id_: str):
    try:
        _id = ObjectId(id_)
    except Exception:
        if CONF["fastapi"].get("debug", False):
            logging.warning("Invalid Object ID")
        raise HTTPException(status_code=400)
    return _id

async def _get_designcard_or_404(id_: str):
    _id = validate_object_id(id_)
    image = await DB.tbl_image.find_one({"_id": _id})
    if image:
        return fix_image_id(image)
    else:
        return HTTPException(status_code=404, detail="Image not found")

def fix_image_id(image):
    image["id_"] = str(image["_id"])
    return image

def randomString(stringLength=6):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

async def image_process(dm: MediaCardBase):
    image = Image.open(dm.origin_name)
    r_width, r_height = image.size
    # print(image.shape)
    height = 310
    width = 488
    # TODO Belum Otomatis Landscape , potrait
    # if width>height:
    if r_width > r_height :
        new_image = image.resize((width, height))
        new_image.save(dm.file_name + 'landscape.' + dm.file_type )
    else :
        new_image = image.resize((height, width))
        new_image.save(dm.file_name + 'potrait.' + dm.file_type )
    # image.thumbnail((size_potrait))
    # image.save(dm.file_name + 'potrait.' + dm.file_type )
    # horizontal, vertical = image.size
    os.remove(dm.origin_name)


# ======================================================================
#

@router_desainkartu.post("/uploadkartu")
async def upload_desainkartu(background_tasks: BackgroundTasks , file: UploadFile = File(...)):
    content_type = file.content_type
    # cek extension file
    if content_type == "image/jpeg" or content_type == "image/jpg" or content_type == "image/png" or content_type == "image/gif":
      dm = MediaCardBase()
      origin_name = randomString(6) + file.filename
      folder = "/home/anton/work/tki/kartu/server/desainkartu/"
      file_location = folder + origin_name
      file_object = file.file
      upload = open(os.path.join(folder, origin_name), 'wb+')
      shutil.copyfileobj(file_object, upload)
      upload.close()
      # proses image di background
      extention = content_type.replace('image/','')
      random = randomString(7)
      dm.name = str(date.today()) + '_' + random + '_'
      new_file_name = folder + dm.name
      dm.createTime = datetime.utcnow()
      dm.updateTime = datetime.utcnow()
      dm.companyId = ''
      dm.creatorId = ''
      dm.origin_name = file_location
      dm.file_name = new_file_name
      dm.file_type = extention
      background_tasks.add_task(image_process, dm)
      # save img data to db    
      DB.tbl_image.insert_one(dm.dict())
      return dm.dict()
    else:
      raise HTTPException(status_code=406, detail="Unknown image Type")


@router_desainkartu.get("/getkartu/{file_name}/{jenis}")
async def get_desainkartu(file_name: str, jenis: str):
    image = await DB.tbl_image.find_one({"name": file_name})
    if image:
        filepath = image["file_name"] + jenis + '.' + image["file_type"]
        return FileResponse(filepath)
    else:
        raise HTTPException(status_code=404, detail="Image not found")
