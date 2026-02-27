from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Literal
from datetime import datetime

CURRENT_YEAR = datetime.now().year


# Modelo: Libro
class Libro(BaseModel):
    id: str
    nombre: str = Field(min_length=2, max_length=100)
    autor: str
    anio: int
    paginas: int
    estado: Literal["disponible", "prestado"] = "disponible"

    @field_validator("anio")
    @classmethod
    def validar_anio(cls, v):
        if v <= 1450 or v > CURRENT_YEAR:
            raise ValueError(f"El año debe ser mayor a 1450 y menor o igual a {CURRENT_YEAR}")
        return v

    @field_validator("paginas")
    @classmethod
    def validar_paginas(cls, v):
        if v < 1:
            raise ValueError("Las páginas deben ser un entero positivo mayor a 1")
        return v


# Modelo: Usuario
class Usuario(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    correo: EmailStr


# Modelo: Préstamo
class Prestamo(BaseModel):
    id: str
    libro_id: str
    usuario: Usuario