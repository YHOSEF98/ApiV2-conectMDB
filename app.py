import os
from fastapi import FastAPI, Body, HTTPException, status 
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from typing import Optional, List
import motor.motor_asyncio
import pymongo


app = FastAPI()
#cliente = motor.motor_asyncio.AsyncIOMotorClient(os.environ[mongodb+srv://yhosefmayorga:1065245907Mc-@cluster0.uidz2ja.mongodb.net/?retryWrites=true&w=majority])

cliente = pymongo.MongoClient("mongodb+srv://yhosefmayorga:1065245907Mc-@cluster0.uidz2ja.mongodb.net/?retryWrites=true&w=majority")
db = cliente.MinTicVehiculos
#db = []
class pyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Vehiculos(BaseModel):
    id: pyObjectId = Field(defaul_factory=pyObjectId, alias="_id")
    Marca: str = Field(...)
    Modelo: int = Field(...)
    Tipo: str = Field(...)
    Precio: int = Field(..., le=10)

    class config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        jsonable_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "Marca": "Mitsubishi",
                "Modelo": 1998,
                "Tipo": "Montero",
                "Precio": 22000000
            }
        }


class UpdateVehiculos(BaseModel):
    Marca: Optional[str]
    Modelo: Optional[int]
    Tipo: Optional[str]
    Precio: Optional[int]

    class config:
        allow_population_by_field_name = True
        arbtrary_types_allowed = True
        jsonable_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "Marca": "Mitsubishi",
                "Modelo": 1998,
                "Tipo": "Montero",
                "Precio": 24000000
            }
        }

@app.post("/carros", response_description="Add new vehiculo", response_model=Vehiculos)
async def create_vehiculo(vehiculo: Vehiculos = Body(...)):
    vehiculo = jsonable_encoder(vehiculo)
    new_vehiculo = await db["Vehiculos"].insert_one(vehiculo)
    created_vehiculo = await db["Vehiculos"].find_one({"_id": new_vehiculo.insert_id})

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_vehiculo)


@app.get("/carros", response_description="Listado de vehiculos", response_model=List[Vehiculos])
async def list_vehiculos():
    vehiculos = await db["Vehiculos"].find().to_list(1000)
    return vehiculos

@app.get("/carros/{id}", response_description="vehiculo encontrado", response_model=Vehiculos)
async def show_vehiculo(id: str):
    if (vehiculo := await db["Vehiculos"].find_one({"_id":id})) is not None:
        return vehiculo
    
    raise HTTPException(status_code=404, detail=f"Vehiculo {id} No encontrado")


@app.put("/carros/{id}", response_description="actualizar vehiculo", response_model=Vehiculos)
async def update_vehiculo(id: str, vehiculo: UpdateVehiculos = Body(...)):
    vehiculo = {k: v for k, v in vehiculo.dict().items() if v is not None}
    if len(vehiculo) >= 1:
        update_result = await db["Vehiculos"].update_one({"_id":id}, {"$set": vehiculo})

        if update_result.modified_count == 1:
            if (
                updated_vehiculo := await db["Vehiculos"].find_one({"_id":id})) is not None:

                return updated_vehiculo
    
    if (existing_student := await db["Vehiculos"].find_one({"_id":id})) is not None:
        return existing_student

    raise HTTPException(status_code=404, detail=f"Vehiculo {id} No encontrado")

@app.put("/carros/{id}", response_description="Borrar vehiculo")
async def delete_vehiculo(id: str):
    delete_result = await db["Vehiculos"].delete_one({"_id":id})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Vehiculo {id} No encontrado")

