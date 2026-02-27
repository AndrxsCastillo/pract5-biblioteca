from fastapi import FastAPI, HTTPException, status
from app.models import Libro, Prestamo


# 2. Inicialización de la APP
app = FastAPI(
    title="API Biblioteca Digital",
    description="Control de libros y préstamos - Práctica 5",
    version="1.0.0"
)

# Base de datos ficticia (listas en memoria)
libros: list[dict] = []
prestamos: list[dict] = []


# Endpoints
@app.get("/", tags=["Inicio"])
async def inicio():
    return {"mensaje": "Bienvenido a la API de Biblioteca Digital"}


# Libros
@app.post("/v1/libros/", tags=["Libros"], status_code=status.HTTP_201_CREATED)
async def registrar_libro(libro: Libro):
    """
    Registra un nuevo libro.
    - 201: Libro registrado correctamente.
    - 400: Faltan datos o el nombre no es válido.
    - 409: El libro ya existe (mismo ID).
    """
    # Verificar que el nombre no esté vacío (pydantic ya valida longitud)
    if not libro.nombre.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre del libro no es válido"
        )

    # Verificar que el ID no esté duplicado
    for lib in libros:
        if lib["id"] == libro.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un libro con ese ID"
            )

    libros.append(libro.model_dump())
    return {
        "mensaje": "Libro registrado correctamente",
        "status": 201,
        "libro": libro
    }


@app.get("/v1/libros/", tags=["Libros"])
async def listar_libros():
    """
    Lista todos los libros disponibles (estado = 'disponible').
    """
    disponibles = [lib for lib in libros if lib["estado"] == "disponible"]
    return {
        "status": 200,
        "total": len(disponibles),
        "data": disponibles
    }


@app.get("/v1/libros/{nombre}", tags=["Libros"])
async def buscar_libro(nombre: str):
    """
    Busca un libro por su nombre (búsqueda parcial, sin distinguir mayúsculas).
    """
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
    """
    Registra el préstamo de un libro a un usuario.
    - 201: Préstamo registrado.
    - 404: Libro no encontrado.
    - 409: El libro ya está prestado.
    """
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

    # Registrar préstamo y actualizar estado del libro
    libro_encontrado["estado"] = "prestado"
    prestamos.append(prestamo.model_dump())

    return {
        "mensaje": "Préstamo registrado correctamente",
        "status": 201,
        "prestamo": prestamo
    }


@app.put("/v1/prestamos/{id}/devolver", tags=["Préstamos"])
async def devolver_libro(id: str):
    """
    Marca un libro como devuelto.
    - 200: Libro devuelto correctamente.
    - 404: Préstamo no encontrado.
    """
    for prestamo in prestamos:
        if prestamo["id"] == id:
            # Cambiar estado del libro a disponible
            for lib in libros:
                if lib["id"] == prestamo["libro_id"]:
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
async def eliminar_prestamo(id: str):
    """
    Elimina el registro de un préstamo.
    - 200: Préstamo eliminado.
    - 409: El registro de préstamo ya no existe.
    """
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