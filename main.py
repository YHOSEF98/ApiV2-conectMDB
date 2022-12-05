import os
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, EmailStr
from bson.objectid import ObjectId
from typing import Optional, List
import motor.motor_asyncio
import pymongo

app = FastAPI()
#client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["mongodb+srv://yhosefmayorga:1065245907Mc-@cluster0.uidz2ja.mongodb.net/?retryWrites=true&w=majority"])
client = pymongo.MongoClient("mongodb+srv://yhosefmayorga:1065245907Mc-@cluster0.uidz2ja.mongodb.net/?retryWrites=true&w=majority")
mydb = client["MinTicVehiculos"]
db = mydb["Vehiculos"]

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, ObjectId):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

        
class VehiculosModel(BaseModel):
    id:  PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    Modelo: int = Field(...)
    Marca: str = Field(...)
    Año: int = Field(...)
    Tipo: str = Field(...)
    Precio: int = Field(..., le=10)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "Modelo":"montero",
                "Marca" : "Mitsubishi",
                "Año": 1998,
                "Tipo": "Montero",
                "Precio": 22000000
 }
 }

class UpdateVehiculosModel(BaseModel):
    Modelo: Optional[int]
    Marca: Optional[str]
    Año: Optional[int]
    Tipo: Optional[str]
    Precio: Optional[int]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "Modelo":"montero",
                "Marca" : "Mitsubishi",
                "Año": 1998,
                "Tipo": "Montero",
                "Precio": 22000000
    }
 }
@app.post("/", response_description="Add new vehiculo", response_model=VehiculosModel)
async def create_vehiculo(vehiculo: VehiculosModel = Body(...)):
    vehiculo = jsonable_encoder(vehiculo)
    new_vehiculo = await db.insert_one(vehiculo)
    created_vehiculo = await db.find_one({"_id":new_vehiculo.inserted_id})

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_vehiculo)


@app.get("/", response_description="List all vehiculo",response_model=List[VehiculosModel])
async def list_vehiculo():
    vehiculo = await db.find().to_list(1000)
    return vehiculo


@app.get("/{id}", response_description="Get a single vehiculo",response_model=VehiculosModel)
async def show_vehiculo(id: str):
    if (vehiculo := await db.find_one({"_id": id})) is not None: return vehiculo

    raise HTTPException(status_code=404, detail=f"vehiculo {id} not found")


@app.put("/{id}", response_description="Update a vehiculo",response_model=VehiculosModel)
async def update_vehiculo(id: str, vehiculot: UpdateVehiculosModel = Body(...)):
    vehiculo = {k: v for k, v in vehiculo.dict().items() if v is not None}
    if len(vehiculo) >= 1:
        update_result = await db.update_one({"_id": id}, {"$set":vehiculo})
        if update_result.modified_count == 1:
            if (updated_vehiculo := await db.find_one({"_id": id})) is not None:

                return updated_vehiculo
    if (existing_vehiculo := await db.find_one({"_id": id})) is not None:
        return existing_vehiculo

    raise HTTPException(status_code=404, detail=f"vehiculo {id} not found")


@app.delete("/{id}", response_description="Delete a vehiculo")
async def delete_vehiculo(id: str):
    delete_result = await db.delete_one({"_id": id})
    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail=f"vehiculo {id} not found")