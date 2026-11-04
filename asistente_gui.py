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