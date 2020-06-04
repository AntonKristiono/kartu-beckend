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
# import cv2

from PIL import Image
from autocrop import Cropper

from .model_image import MediaBase

router_image = APIRouter()
cropper = Cropper()



def validate_object_id(id_: str):
    try:
        _id = ObjectId(id_)
    except Exception:
        if CONF["fastapi"].get("debug", False):
            logging.warning("Invalid Object ID")
        raise HTTPException(status_code=400)
    return _id


async def _get_image_or_404(id_: str):
    _id = validate_object_id(id_)
    image = await DB.tbl_image.find_one({"_id": _id})
    if image:
        return fix_image_id(image)
    else:
        raise HTTPException(status_code=404, detail="Image not found")


def fix_image_id(image):
    image["id_"] = str(image["_id"])
    return image


def randomString(stringLength=6):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def image_process(dm: MediaBase):
    # Cropper Wizard
    # cropper = Cropper()
    # print(dm.origin_name)
    cropped_array = cropper.crop(dm.origin_name)
    cropped_image = Image.fromarray(cropped_array)
    cropped_image.save(dm.file_name + 'facecrop.' + dm.file_type)
    #
    image = Image.open(dm.origin_name)
    # resize std
    image.thumbnail((800, 800))
    image.save(dm.file_name + 'std.' + dm.file_type)
    # resize thumb
    image.thumbnail((400, 400))
    image.save(dm.file_name + 'thumb.' + dm.file_type)
    # horizontal, vertical = image.size
    # if horizontal>vertical:
    #     ico_max = 150 * horizontal / vertical
    #     image.thumbnail((ico_max, ico_max))
    #     horizontal, vertical = image.size
    #     jarak1 = (horizontal - 150) / 2
    #     jarak2 = jarak1 + 150
    #     box = (jarak1, 0, jarak2, 150)
    #     image_crop = image.crop(box)
    #     image_crop.save(dm.file_name + 'ico.' + dm.file_type)
    # else:
    #     ico_max = 150 * vertical / horizontal
    #     image.thumbnail((ico_max, ico_max))
    #     horizontal, vertical = image.size
    #     jarak1 = (vertical - 150) / 2
    #     jarak2 = jarak1 + 150
    #     box = (0, jarak1, 150, jarak2)
    #     image_crop = image.crop(box)
    #     image_crop.save(dm.file_name + 'ico.' + dm.file_type)
        # resize icon im.crop((left, top, right, bottom))
    os.remove(dm.origin_name)

# =================================================================================


@router_image.post("/uploadfile")
async def upload_image(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    content_type = file.content_type
    # cek file extension png jpg jpeg gif namafile: 20_04_25_750x500_abcdefgh
    if content_type == "image/jpeg" or content_type == "image/jpg" or content_type == "image/png" or content_type == "image/gif":
        dm = MediaBase()
        origin_name = randomString(6) + file.filename
        # folder = "/root/piton/pro_sopan/images/"
        folder = "/home/anton/work/tki/kartu/beck-end/datafoto/"
        file_location = folder + origin_name
        file_object = file.file
        upload = open(os.path.join(folder, origin_name), 'wb+')
        shutil.copyfileobj(file_object, upload)
        upload.close()
        # proses image di background
        extention = content_type.replace('image/', '')
        random = randomString(8)
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
        # save image data to db
        DB.tbl_image.insert_one(dm.dict())
        return dm.dict()
    else:
        raise HTTPException(status_code=406, detail="Unknown image type")

@router_image.post("/uploadBulkFile")
async def upload_image(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    content_type = file.content_type
    # cek file extension png jpg jpeg gif namafile: 20_04_25_750x500_abcdefgh
    if content_type == "image/jpeg" or content_type == "image/jpg" or content_type == "image/png" or content_type == "image/gif":
        dm = MediaBase()
        origin_name = randomString(6) + file.filename
        # folder = "/root/piton/pro_sopan/images/"
        folder = "/home/anton/work/tki/kartu/beck-end/datafoto/"
        file_location = folder + origin_name
        file_object = file.files
        upload = open(os.path.join(folder, origin_name), 'wb+')
        shutil.copyfileobj(file_object, upload)
        upload.close()
        # proses image di background
        extention = content_type.replace('image/', '')
        random = randomString(8)
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
        # save image data to db
        DB.tbl_image.insert_many(dm.dict())
        # return dm.dict()
        return {"filenames": [file.filename for file in files]}
    else:
        raise HTTPException(status_code=406, detail="Unknown image type")


@router_image.get("/get/{file_name}/{jenis}")
async def get_image(file_name: str, jenis: str):
    image = await DB.tbl_image.find_one({"name": file_name})
    if image:
        filepath = image["file_name"] + jenis + '.' + image["file_type"]
        return FileResponse(filepath)
    else:
        raise HTTPException(status_code=404, detail="Image not found")
