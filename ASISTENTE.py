#!/usr/bin/env python
# coding: utf-8

# # Ejercicio adicional de fin de semana: semana 2
# 
# Ahora usa todo lo que aprendiste en la semana 2 para construir un prototipo completo para la pregunta/respuesta técnica que creaste en el ejercicio de la semana 1.
# 
# Esto debería incluir una interfaz de usuario de Gradio, transmisión, uso del mensaje del sistema para agregar experiencia y la capacidad de cambiar entre modelos. ¡Puntos extra si puedes demostrar el uso de una herramienta!
# 
# Si te sientes audaz, ve si puedes agregar una entrada de audio para poder hablarle y hacer que responda con audio. ChatGPT o Claude pueden ayudarte, o envíame un correo electrónico si tienes preguntas.
# 
# Pronto publicaré una solución completa aquí, a menos que alguien se me adelante...
# 
# Hay tantas aplicaciones comerciales para esto, desde un tutor de idiomas hasta una solución de incorporación de empresas, pasando por una IA complementaria para un curso (¡como este!). No puedo esperar a ver tus resultados.

# In[7]:


### Vamos con semana 2

import os
import requests
from bs4 import BeautifulSoup
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
import google.generativeai
import anthropic


# In[8]:


import gradio as gr


# In[9]:


# Un mensaje genérico del sistema: ¡no más IA adversarias sarcásticas!

system_message="Eres un experto en programación y análisis de código. Responde fácil, apto para no expertos y con precisión, por favor pon los resultados con salto de línea."


# In[10]:


def stream(prompt):
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
      ]
    stream = openai.chat.completions.create(
        model='gpt-4o-mini',
        messages=messages,
        stream=True
    )
    result = ""
    for chunk in stream:
        result += chunk.choices[0].delta.content or ""
        yield result


# In[11]:


view = gr.Interface(
    fn=stream,
    inputs=[gr.Textbox(label="Haz una pregunta de codigo:", lines=6)],
    outputs=[gr.Textbox(label="Respuesta:", lines=8)],
    flagging_mode="never"
)
view.launch()


# In[12]:


#Es bien sabido que Claude es la herramienta fav de Cientificxs de datos asi que agrego a Claude como opción para
#dar rta too

claude = anthropic.Anthropic()

def stream_2(prompt):
    result = claude.messages.stream(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        temperature=0.7,
        system=system_message,
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    response = ""
    with result as stream:
        for text in stream.text_stream:
            response += text or ""
            yield response


# In[13]:


def stream_model(prompt, model):
    if model=="GPT":
        result = stream(prompt)
    elif model=="Claude":
        result = stream_2(prompt)
    else:
        raise ValueError("Modelo Desconocido")
    yield from result


# In[14]:


view = gr.Interface(
    fn=stream_model,
    inputs=[gr.Textbox(label="Haz una pregunta de codigo:"), gr.Dropdown(["GPT", "Claude"], label="Selecciona un modelo:", value="GPT")],
    outputs=[gr.Markdown(label="Respuesta:")],
    flagging_mode="never"
)
view.launch()


# In[15]:


import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr


# In[16]:


#vamos al chatbot> cambiamos ligeramente el objetivo del chat para no solo ser un asistente sino para ofrecerle
#al usuario comprar un curso
system_message = "Eres un asistente de programacion, tu conocimiento es completo pero limitado. \
Es por eso que debes tratar de alentar gentilmente al alumno a que revise los cursos disponibles en la plataforma Estudio3\
Por ejemplo, si el alumno dice 'No termino de entender el codigo', \
podrías responder algo como 'Genial, tenemos muchos cursos disponibles en Estudio3 que podrian ser perfectos para vos'. \
Anima al cliente a comprar cursos haciendo incapie en que es personalizado, on demand y que obtendra un certificado."


# In[17]:


def chat(message, history):
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]

    stream = openai.chat.completions.create(model='gpt-4o-mini', messages=messages, stream=True)

    response = ""
    for chunk in stream:
        response += chunk.choices[0].delta.content or ''
        yield response


# In[ ]:





# In[ ]:





# In[18]:


gr.ChatInterface(fn=chat, type="messages").launch()


# In[ ]:





# In[19]:


# Agregar una herramienta para dar opciones de cursos y precios

cursos_disponibles = {"python": "10K", "r": "5k", "java": "10k", "sql": "5k","python": "10K"}

def get_course_price(lenguaje_seleccionado):
    print(f"Se solicitó la herramienta get_course_price para {lenguaje_seleccionado}")
    lenguaje = lenguaje_seleccionado.lower()
    return cursos_disponibles.get(lenguaje, "Unknown")


# In[20]:


paquetes_disponibles = {"python": "50 horas", "r": "18 horas", "java": "25 horas", "sql": "25 horas","python": "50 horas"}


def get_course_length(lenguaje_seleccionado):
    print(f"Se solicitó la herramienta get_course_lenght para {lenguaje_seleccionado}")
    lenguaje = lenguaje_seleccionado.lower()
    return paquetes_disponibles.get(lenguaje, "Unknown")


# In[21]:


# dar herramienta para que el alumno pueda mandar un mail a Estudio3
import smtplib
from email.mime.text import MIMEText

def create_email_template(nombre, email, mensaje):
    print(f"Se solicitó enviar un email de {nombre} ({email}) con el mensaje: {mensaje}")

    # Configurar el cuerpo del mensaje
    msg = MIMEText(f"Nombre: {nombre}\nEmail: {email}\nMensaje: {mensaje}")
    msg["Subject"] = asunto
    msg["From"] = remitente
    msg["To"] = destinatario


# In[22]:


# Hay una estructura de diccionario particular que se requiere para describir nuestra función:
# es un diccionario
price_function = {
    "name": "get_course_price", # aca va el nombre de la funcion
    "description": "Obtén el precio de un curso de programación. Llámalo siempre que necesites saber el precio del curso, por ejemplo, cuando un cliente pregunte '¿Cuánto cuesta un curso de este lenguaje?'",
    #va en el idioma del LLM q le dara al modelo para que es adecuado utilizar esta funcion
    #darle un ejemplo es una muy buena idea
    "parameters": {
        #se describe la función en si
        "type": "object",
        "properties": {
            "lenguaje_seleccionado": {
                "type": "string",
                "description": "El lenguaje que deseas aprender",
            },
        },
        #parametro requerido y obligatorio
        "required": ["lenguaje_seleccionado"],
        "additionalProperties": False
    }
}


# In[23]:


email_template = {
    "name": "create_email_template",
    "description": "Crea una plantilla para solicitar más información sobre los cursos disponibles.",
    "parameters": {
        "type": "object",
        "properties": {
            "nombre": {
                "type": "string",
                "description": "Nombre del solicitante"
            },
            "email": {
                "type": "string",
                "description": "Correo electrónico del solicitante"
            },
            "mensaje": {
                "type": "string",
                "description": "Mensaje con la solicitud de información"
            }
        },
        "required": ["nombre", "email", "mensaje"],
        "additionalProperties": False
    }
}


# In[24]:


# Hay una estructura de diccionario particular que se requiere para describir nuestra función:
# es un diccionario
length_function = {
    "name": "get_course_length", # aca va el nombre de la funcion
    "description": "Obtén la duracion un curso de programación. Llámalo siempre que necesites saber la duración curso, por ejemplo, cuando un cliente pregunte '¿Cuánto horas puedo estudiar ese lenguaje?'",
    #va en el idioma del LLM q le dara al modelo para que es adecuado utilizar esta funcion
    #darle un ejemplo es una muy buena idea
    "parameters": {
        #se describe la función en si
        "type": "object",
        "properties": {
            "lenguaje_seleccionado": {
                "type": "string",
                "description": "La duración del curso del lenguaje que deseas aprender",
            },
        },
        #parametro requerido y obligatorio
        "required": ["lenguaje_seleccionado"],
        "additionalProperties": False
    }
}


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[25]:


#Generacion de las herramientas

tools = [{"type": "function", "function": price_function},{"type": "function", "function": length_function},
        {"type": "function", "function": email_template}]


# In[ ]:





# In[ ]:





# In[26]:


def handle_tool_call(message):
    tool_call = message.tool_calls[0] # recuperamos la herramienta q quieres usar
    arguments = json.loads(tool_call.function.arguments) #cargamos los argumentos
    lenguaje = arguments.get('lenguaje_seleccionado') #argumentos mandatorios


## aca agrego opciones para el uso de las dos tools   
    if tool_call.function.name == "get_course_price":
        result = get_course_price(lenguaje)
    elif tool_call.function.name == "get_course_length":
        result = get_course_length(lenguaje)
    elif tool_call.function.name == "create_email_template":
        result = create_email_template(arguments.get("nombre"), arguments.get("email"), arguments.get("mensaje"))
    else:
        result = "Unknown tool"

    response = {
        "role": "tool",
        "content": json.dumps({"lenguaje_seleccionado": lenguaje, "result": result}),
        "tool_call_id": tool_call.id
    }
    return response, arguments.get("nombre")


# In[27]:


def chat(message, history):
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model='gpt-4o-mini', messages=messages, tools=tools)
    
    # se agregaron las tools en el codigo que ya conocemos
    #comprobamos si la rta tiene un finish reason - es donde integramos la herramienta
    #if == tool_calls
    # al agregarla lo estamos mandando al modelo
    # 
    if response.choices[0].finish_reason=="tool_calls":
        message = response.choices[0].message #recopilamos la rta
        response, lenguaje = handle_tool_call(message) #aca debemos programar la llamada a la herramienta, la funcion esta abajo 
        #esta ejecuta la parte de los precios y esa es la rta q apendeo abajo
        messages.append(message) # a partir de ese mensaje se deben eppendear al resto de los mensajes
        messages.append(response) #a ca agregamos la respuesta 
        response = openai.chat.completions.create(model='gpt-4o-mini', messages=messages) # es la segunda rta de open ia a partir de la herramienta
        # rta final
        # flujo : usuario, asistente, usuario, asistente q quiere llamar a herramienta 
    
    return response.choices[0].message.content


# In[ ]:





# In[28]:


gr.ChatInterface(fn=chat, type="messages").launch()


# In[ ]:





# In[32]:


pip install nbconvert

nbconvert --to script week2 EXERCISE.ipynb

