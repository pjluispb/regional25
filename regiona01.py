import streamlit as st
import requests
import notion_client
import json

# --- Configuración Notion ---
NOTION_TOKEN = notion_client.Client(auth = st.secrets["notion"]["authkey"])
DB_ID = st.secrets["notion"]["Regional_databaseID"]
notion = NOTION_TOKEN

# --- Lectura de parámetros en la URL ---
params = st.query_params
nombre_prellenado = params.get('nombre').replace('%20', ' ')
telefono_prellenado = params.get('telefono', [''])

@st.dialog("Alerta debes seleccionar un rol")
def alerta1():
    st.write(f"Debes seleccionar un rol para continuar")

def buscar_usuario(telefono):
    resultados = notion.databases.query(
        database_id=DB_ID,
        filter={
            "property": "Telefono",
            "phone_number": {"equals": telefono},
        }
    )
    return resultados['results'][0] if resultados['results'] else None


def actualizar_usuario(page_id, datos, cambios):
    notion.pages.update(
        page_id=page_id,
        properties=datos
    )
    notion.pages.update(
        page_id=page_id,
        properties={"Cambios": {"number": cambios + 1}}
    )

def crear_usuario(datos):
    notion.pages.create(
        parent={"database_id": DB_ID},
        properties=datos
    )

def datos_a_notion(nombre, telefono, rol, iglesia, ciudad, cambios):
    return {
        "Nombre": {"title": [{"text": {"content": nombre}}]},
        "Telefono": {"phone_number": telefono},
        "Rol": {"select": {"name": rol}},
        "Iglesia": {"rich_text": [{"text": {"content": iglesia}}]},
        "Ciudad": {"rich_text": [{"text": {"content": ciudad}}]},
        "Cambios": {"number": cambios}
    }

ubusa = buscar_usuario(telefono_prellenado)
if ubusa != None:
    #f"ubusa properties = {ubusa['properties']}"
    rolbd = ubusa['properties']['Rol']['select']['name']
    ciudadbd = ubusa['properties']['Ciudad']['rich_text'][0]['text']['content']
    cambiosbd = ubusa['properties']['Cambios']['number'] if ubusa['properties']['Cambios']['number']!=None else 1
    iglesiabd = ubusa['properties']['Iglesia']['rich_text'][0]['text']['content']
    telefonobd = ubusa['properties']['Telefono']['phone_number']
    nombrebd = ubusa['properties']['Nombre']['title'][0]['text']['content']
else:
    rolbd = None
    ciudadbd = None
    cambiosbd = 0
    iglesiabd = None
    telefonobd = 0
    nombrebd = None

st.header("Bienvenido al registro de la Regional 2025")

with st.form('Registro 1'):
    st.subheader("Elije tu rol en esta regional")
    optionsrol = ["Ministro", "Delegado", "Invitado", "Voluntario"]
    if rolbd != None:
        rol = st.radio("Selección:", optionsrol, index=optionsrol.index(rolbd))
    else: rol = st.radio("Selección:", optionsrol, index = None)

    st.subheader("Confirma/Edita tu nombre y número de whatsapp")

    nombre = st.text_input("Nombre :", value= nombrebd if nombrebd != None else nombre_prellenado, help="Escribe tu nombre completo", disabled=False, placeholder=nombre_prellenado)
    telefono = st.text_input("#whatsapp :", value= telefonobd if telefonobd != 0 else telefono_prellenado, help="Escribe tu número de WhatsApp", disabled=False, placeholder=telefono_prellenado)
    iglesia = st.text_input("Iglesia :", value= iglesiabd, placeholder='Nombre de la iglesia')
    ciudad = st.text_input("Ciudad :", value= ciudadbd, placeholder='Nombre de la Ciudad')

    st.write("")  
    submitted = st.form_submit_button("Enviar")

    if submitted:
        
        datos = datos_a_notion(nombre, telefono, rol, iglesia, ciudad, cambiosbd+1)
        if datos["Rol"]['select']['name'] != None:
            usuario_existente = buscar_usuario(telefono)
            if usuario_existente:
                propiedades = usuario_existente["properties"]
                cambios_actuales = propiedades.get("Cambios", {}).get("number", 0)
                cambios = sum([
                    propiedades.get("Nombre", {}).get("title", [{}])[0].get("text", {}).get("content", "") != nombre,
                    propiedades.get("Iglesia", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "") != iglesia,
                    propiedades.get("Ciudad", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "") != ciudad,
                    propiedades.get("Rol", {}).get("select", {}).get("name", "") != rol
                ])
                if cambios and cambios_actuales < 3:
                    actualizar_usuario(usuario_existente["id"], datos, cambios_actuales)
                    st.success(f"¡Datos actualizados y confirmados! Cambios realizados: {cambios_actuales + 1}")
                elif cambios_actuales >= 3:
                    st.error("¡Ya no se permiten más cambios a tus datos por este medio!")
                else:
                    st.info("Tus datos ya estaban actualizados.")
            else:
                crear_usuario(datos)
                st.success("¡Registro exitoso!")
        else:
            alerta1()


'---'
