from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import select
import os
import uuid
import boto3
from fastapi import File, UploadFile

from src.models.product_model import Product, ProductCategories
from src.shared.database.session_db import SessionDep

app = FastAPI()

s3_client = boto3.client("s3", region_name="us-east-2")
S3_BUCKET_NAME = "fastapi-s3-app-bucket"
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


class CreateProduct(BaseModel):
    name: str = Field(min_length=1)
    price: float = Field(gt=0)
    quantity: int = Field(gt=0)
    category: ProductCategories


@app.post("/product", status_code=201)
def create_product(data: CreateProduct, session: SessionDep):
    # Normalizar una sola vez: lo que se busca es lo que se guarda
    name = data.name.lower().strip()
    if not name:
        raise HTTPException(status_code=422, detail="El nombre no puede estar vacío")

    existing = session.exec(select(Product).where(Product.name == name)).first()
    if existing is not None:
        raise HTTPException(
            status_code=409, detail="El producto ya existe en la base de datos"
        )

    product = Product(
        name=name,
        category=data.category,
        price=data.price,
        quantity=data.quantity,
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@app.get("/product")
def get_products(session: SessionDep):
    return session.exec(select(Product)).all()


@app.delete("/product/{product_id}", status_code=204)
def delete_product(product_id: int, session: SessionDep):
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    session.delete(product)
    session.commit()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/images", status_code=201)
async def upload_image(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=422,
            detail="Tipo de archivo no permitido. Solo JPEG, PNG o WEBP.",
        )

    extension = file.filename.split(".")[-1]
    key = f"images/{uuid.uuid4()}.{extension}"

    s3_client.upload_fileobj(file.file, S3_BUCKET_NAME, key)

    return {
        "message": "Imagen subida correctamente",
        "key": key,
        "url": f"https://{S3_BUCKET_NAME}.s3.us-east-2.amazonaws.com/{key}",
    }
