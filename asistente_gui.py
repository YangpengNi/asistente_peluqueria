import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext

from dotenv import load_dotenv
from google import genai

# Localizamos la carpeta del proyecto para encontrar .env y servicios.txt.

CARPETA_PROYECTO = Path(__file__).resolve().parent

# Cargamos la clave desde .env para no escribirla directamente en el código.
load_dotenv(CARPETA_PROYECTO / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")
MODELO = "gemini-3.8-flash"

# Creamos el cliente de Gemini solamente si se encontró la clave.
cliente = genai.Client(api_key=API_KEY) if API_KEY else None

# Leemos los servicios que ofrecemos en la peluquería.
def leer_servicios():
    ruta_servicios = CARPETA_PROYECTO / "servicios.txt"

    if not ruta_servicios.exists():
        raise FileNotFoundError("No se encontró el archivo servicios.txt")

    return ruta_servicios.read_text(encoding="utf-8")

# Consultamos Gemini usando los servicios como contexto.
def consultar_gemini(pregunta):
    if cliente is None:
        raise RuntimeError(
            "No se encontró GEMINI_API_KEY en el archivo .env"
        )

    servicios = leer_servicios()

    # Construimos el prompt con reglas para evitar respuestas inventadas.
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

# Escribimos los mensajes en el historial del chat.
def escribir_chat(autor, mensaje, etiqueta):
    historial.config(state="normal")
    historial.insert(tk.END, f"{autor}: ", etiqueta)
    historial.insert(tk.END, f"{mensaje}\n\n")
    historial.see(tk.END)
    historial.config(state="disabled")

# Reactivamos la interfaz cuando termina la llamada a Gemini.
def finalizar_consulta(respuesta, es_error=False):
    etiqueta = "error" if es_error else "asistente"
    autor = "Error" if es_error else "Asistente"

    escribir_chat(autor, respuesta, etiqueta)
    boton_enviar.config(state="normal")
    estado.config(text="Preparado")
    entrada.focus()


# Recibimos y validamos la pregunta escrita por el usuario.
def enviar_pregunta(event=None):
    pregunta = entrada.get().strip()
    if not pregunta:
        messagebox.showwarning(
            "Pregunta vacía",
            "Escribe una pregunta antes de pulsar Enviar.",
        )
        return

    escribir_chat("Tú", pregunta, "usuario")
    entrada.delete(0, tk.END)

    boton_enviar.config(state="disabled")
    estado.config(text="Consultando a Gemini...")
    hilo = threading.Thread(
        target=procesar_consulta,
        args=(pregunta,),
        daemon=True,
    )
    hilo.start()

# Ejecutamos la consulta en segundo plano para no congelar la ventana.
def procesar_consulta(pregunta):
    try:
        respuesta = consultar_gemini(pregunta)
        ventana.after(0, finalizar_consulta, respuesta, False)
    except Exception as error:
        mensaje = f"No se pudo obtener una respuesta: {error}"
        ventana.after(0, finalizar_consulta, mensaje, True)


# Creamos la ventana principal fuera de las funciones.
ventana = tk.Tk()
ventana.title("Asistente de Peluquería")
ventana.geometry("750x550")
ventana.minsize(600, 400)

titulo = tk.Label(
    ventana,
    text="Asistente virtual de la peluquería",
    font=("Arial", 17, "bold"),
)
titulo.pack(pady=(15, 10))

# El historial tiene scroll y está bloqueado para que el usuario no lo edite.
historial = scrolledtext.ScrolledText(
    ventana,
    wrap=tk.WORD,
    font=("Arial", 11),
    state="disabled",
)
historial.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

historial.tag_config("usuario", foreground="#1746d1", font=("Arial", 11, "bold"))
historial.tag_config("asistente", foreground="#16803c", font=("Arial", 11, "bold"))
historial.tag_config("error", foreground="#c62828", font=("Arial", 11, "bold"))

# Agrupamos el campo de entrada y el botón en la parte inferior.
zona_entrada = tk.Frame(ventana)
zona_entrada.pack(fill=tk.X, padx=15, pady=10)

entrada = tk.Entry(zona_entrada, font=("Arial", 12))
entrada.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
entrada.bind("<Return>", enviar_pregunta)

boton_enviar = tk.Button(
    zona_entrada,
    text="Enviar",
    font=("Arial", 11, "bold"),
    command=enviar_pregunta,
)
boton_enviar.pack(side=tk.RIGHT)

estado = tk.Label(ventana, text="Preparado", anchor="w")
estado.pack(fill=tk.X, padx=15, pady=(0, 10))

escribir_chat(
    "Asistente",
    "¡Hola! Pregúntame por nuestros servicios, precios u horarios.",
    "asistente",
)

entrada.focus()
ventana.mainloop()
