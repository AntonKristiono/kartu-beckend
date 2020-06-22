from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.router_kartu import router_kartu
from routes.router_image import router_image
from routes.router_desainkartu import router_desainkartu
from routes.router_bulkDataKartu import router_bulkDataKartu
from config import config

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_kartu, prefix="/kartu", tags=["info data kartu"], responses={404: {"description": "Not found"}})
app.include_router(router_image, prefix="/image", tags=["foto"], responses={404: {"description": "Not found"}})
app.include_router(router_desainkartu, prefix="/desainkartu", tags=["desain kartu"], responses={404: {"description": "Not found"}})
app.include_router(router_bulkDataKartu, prefix="/uploadDataKartu", tags=["upload data kartu"], responses={404: {"description": "Not found"}})

@app.on_event("startup")
async def app_startup():
    # This if fact does nothing its just an example.
    config.load_config()


@app.on_event("shutdown")
async def app_shutdown():
    # This does finish the DB driver connection.
    config.close_db_client()
