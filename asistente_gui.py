import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext

from dotenv import load_dotenv
from google import genai

##Localizamos la carpeta del proyecto /asistente_peluqueria
## whole el contenido de dentro

CARPETA_PROYECTO = Path(__file__).resolve().parent

##Cargar API_KEY
load_dotenv(CARPETA_PROYECTO / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")
MODELO = "gemini-3.8-flash"

##Creamos el cliente de Gemini
cliente = genai.Client(api_key=API_KEY) if API_KEY else None

##Lectura del servicio que ofrecemos en nuestra peluquería
def leer_servicios():
    ruta_servicios = CARPETA_PROYECTO / "servicios.txt"

    if not ruta_servicios.exists():
        raise FileNotFoundError("No se encontró el archivo servicios.txt")

    return ruta_servicios.read_text(encoding="utf-8")

##Consulta a Gemini
def consultar_gemini(pregunta):
    if cliente is None:
        raise RuntimeError(
            "No se encontró GEMINI_API_KEY en el archivo .env"
        )

    servicios = leer_servicios()

    ##Construcción de prompt

    prompt = f"""
    Eres el asistente virtual de una peluquería.

    REGLAS:
    - Responde únicamente con la información incluida en el contexto.
    - No inventes servicios, precios ni horarios.
    - Si no conoces la respuesta, indícalo claramente.
    - Responde en español.

    CONTEXTO:
    {servicios}

    PREGUNTA:
    {pregunta}
    """

    respuesta = cliente.models.generate_content(
        model=MODELO,
        contents=prompt,
    )

    if not respuesta.text:
        raise RuntimeError("Gemini no devolvió una respuesta de texto")

    return respuesta.text.strip()