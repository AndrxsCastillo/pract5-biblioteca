from fastapi import FastAPI, HTTPException, status
from typing import Literal
from pydantic import BaseModel, EmailStr, Field

# Inicialización de la APP
app = FastAPI(
    title="API Biblioteca Digital",
    description="Control de libros y préstamos - Práctica 5",
    version="1.0.0"
)

# Base de datos ficticia
libros: list[dict] = []
prestamos: list[dict] = []


# Modelos de validación
class Usuario(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre entre 2 y 100 caracteres")
    correo: EmailStr = Field(..., description="Correo electrónico válido")

class Libro(BaseModel):
    id: int = Field(..., gt=0, description="Identificador del libro")
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre entre 2 y 100 caracteres")
    autor: str = Field(..., min_length=2, max_length=100, description="Nombre entre 2 y 100 caracteres")
    año: int = Field(..., gt=1450, le=2026, description="Año mayor a 1450 y menor o igual a 2026")
    paginas: int = Field(..., gt=1, description="Número de páginas mayor a 1")
    estado: Literal["disponible", "prestado"] = "disponible"

class Prestamo(BaseModel):
    id: int = Field(..., gt=0, description="Identificador del préstamo")
    libro_id: int = Field(..., gt=0, description="ID de libro existente")
    usuario: Usuario = Field(..., description="Nombre y correo de usuario")


# Endpoints
@app.get("/", tags=["Inicio"])
async def inicio():
    return {"mensaje": "Bienvenido a la API de Biblioteca Digital"}


# Libros
@app.post("/v1/libros/", tags=["Libros"], status_code=status.HTTP_201_CREATED)
async def registrar_libro(libro: Libro):
    # Verificar ID duplicado
    for lib in libros:
        if lib["id"] == libro.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un libro con ese ID"
            )
    # Verificar nombre válido
    if not libro.nombre.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre del libro no es válido"
        )
    libros.append(libro.model_dump())
    return {
        "mensaje": "Libro registrado correctamente",
        "status": 201,
        "libro": libro
    }


@app.get("/v1/libros/", tags=["Libros"])
async def listar_libros():
    disponibles = [lib for lib in libros if lib["estado"] == "disponible"]
    return {
        "status": 200,
        "total": len(disponibles),
        "data": disponibles
    }


@app.get("/v1/libros/{nombre}", tags=["Libros"])
async def buscar_libro(nombre: str):
    resultados = [
        lib for lib in libros
        if nombre.lower() in lib["nombre"].lower()
    ]
    if not resultados:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró ningún libro con ese nombre"
        )
    return {
        "status": 200,
        "total": len(resultados),
        "data": resultados
    }


# Préstamos
@app.post("/v1/prestamos/", tags=["Préstamos"], status_code=status.HTTP_201_CREATED)
async def registrar_prestamo(prestamo: Prestamo):
    # Buscar el libro
    libro_encontrado = None
    for lib in libros:
        if lib["id"] == prestamo.libro_id:
            libro_encontrado = lib
            break

    if not libro_encontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado"
        )
    # Verificar disponibilidad
    if libro_encontrado["estado"] == "prestado":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El libro ya está prestado"
        )

    libro_encontrado["estado"] = "prestado"
    prestamos.append(prestamo.model_dump())
    return {
        "mensaje": "Préstamo registrado correctamente",
        "status": 201,
        "prestamo": prestamo
    }


@app.put("/v1/prestamos/{id}/devolver", tags=["Préstamos"])
async def devolver_libro(id: int):
    for prestamo in prestamos:
        if prestamo["id"] == id:

            # Cambiar estado del libro a disponible
            for lib in libros:
                if lib["id"] == prestamo.get("libro_id"):
                    lib["estado"] = "disponible"
                    break
            return {
                "mensaje": "Libro devuelto correctamente",
                "status": 200,
                "prestamo_id": id
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No se encontró el registro de préstamo"
    )


@app.delete("/v1/prestamos/{id}", tags=["Préstamos"])
async def eliminar_prestamo(id: int):
    for prestamo in prestamos:
        if prestamo["id"] == id:
            prestamos.remove(prestamo)
            return {
                "mensaje": "Registro de préstamo eliminado correctamente",
                "status": 200,
                "id_eliminado": id
            }

    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="El registro de préstamo ya no existe"
    )