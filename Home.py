import streamlit as st
import pandas as pd
from openpyxl import load_workbook, Workbook
import json
from datetime import datetime
import pytz
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
import requests
from PIL import Image
from io import BytesIO
import os
import re
from fpdf import FPDF  # Para la generación de PDF

# ===============================
# Configuración de la Página (ESTO DEBE IR AL PRINCIPIO)
# ===============================
st.set_page_config(page_title="🛍 Módulo de Ventas", layout="wide")

# ===============================
# Inicialización del Estado de Sesión
# ===============================

# Inicializar el estado del pedido y el stock si no existen
if 'pedido' not in st.session_state:
    st.session_state.pedido = []

# Inicializar 'df_productos' si no existe
if 'df_productos' not in st.session_state:
    file_path_productos = 'archivo_modificado_productos_20240928_201237.xlsx'  # Archivo de productos
    if os.path.exists(file_path_productos):
        try:
            st.session_state.df_productos = pd.read_excel(file_path_productos)
        except Exception as e:
            st.error(f"Error al cargar el archivo de productos: {e}")
            st.stop()
    else:
        st.warning(f"⚠️ El archivo {file_path_productos} no existe. Por favor, súbelo desde el módulo Productos.")
        st.session_state.df_productos = pd.DataFrame()  # DataFrame vacío

# Inicializar 'df_clientes' si no existe
if 'df_clientes' not in st.session_state:
    file_path_clientes = 'archivo_modificado_clientes_20240928_200050.xlsx'  # Archivo de clientes
    if os.path.exists(file_path_clientes):
        try:
            st.session_state.df_clientes = pd.read_excel(file_path_clientes)
        except Exception as e:
            st.error(f"Error al cargar el archivo de clientes: {e}")
            st.stop()
    else:
        st.warning(f"⚠️ El archivo {file_path_clientes} no existe. Por favor, súbelo desde el módulo Convertidor de CSV.")
        st.session_state.df_clientes = pd.DataFrame()  # DataFrame vacío

# Inicializar 'df_equipo' si no existe
if 'df_equipo' not in st.session_state:
    file_path_equipo = 'equipo.xlsx'
    if os.path.exists(file_path_equipo):
        try:
            st.session_state.df_equipo = pd.read_excel(file_path_equipo)
        except Exception as e:
            st.error(f"Error al cargar el archivo de equipo: {e}")
            st.stop()
    else:
        # Definir los miembros del equipo
        data_equipo = {
            'Nombre': [
                'Joni', 'Eduardo', 'Johan', 'Martin',
                'Marian', 'Sofi', 'Valen', 'Emily',
                'Maria-Jose', 'Vasco'
            ],
            'Rol': [
                'Presidente', 'Gerente General', 'Jefe de Depósito', 'Armar Pedidos',
                'Vendedora', 'Vendedora', 'Vendedora', 'Vendedora',
                'Fotógrafa y Catalogador', 'Super Admin'
            ],
            'Departamento': [
                'Dirección', 'Dirección', 'Depósito', 'Depósito',
                'Ventas', 'Ventas', 'Ventas', 'Ventas',
                'Marketing', 'Dirección'
            ],
            'Nivel de Acceso': [
                'Alto', 'Alto', 'Medio', 'Medio',
                'Bajo', 'Bajo', 'Bajo', 'Bajo',
                'Medio', 'Super Admin'
            ]
        }
        st.session_state.df_equipo = pd.DataFrame(data_equipo)
        # Guardar el DataFrame inicial en Excel
        try:
            st.session_state.df_equipo.to_excel(file_path_equipo, index=False)
        except Exception as e:
            st.error(f"Error al guardar el archivo de equipo: {e}")

# Inicializar 'usuario' en sesión si no existe
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

# ===============================
# Función de Autenticación con Autocompletado y Logo
# ===============================

def login():
    # Mostrar el logo en la parte superior de la barra lateral con tamaño reducido
    st.sidebar.image("logomundo.png", width=230)  # Ajusta el ancho de la imagen al 50% (puedes ajustar según sea necesario)

    st.sidebar.title("🔒 Iniciar Sesión")

    # Selectbox con las opciones de nombres disponibles
    nombre_seleccionado = st.sidebar.selectbox(
        "Selecciona tu nombre",
        [""] + st.session_state.df_equipo['Nombre'].tolist(),
        key="nombre_seleccionado",
        help="Selecciona tu nombre de la lista."
    )

    # Solo mostrar el campo de contraseña y el botón si se selecciona un nombre
    if nombre_seleccionado:
        # Campo de contraseña (opcional)
        password = st.sidebar.text_input("Contraseña", type="password", key="password")
        
        # Botón para iniciar sesión
        if st.sidebar.button("Iniciar Sesión"):
            if nombre_seleccionado == 'Vasco' and password == '74108520':
                usuario_data = st.session_state.df_equipo[st.session_state.df_equipo['Nombre'] == nombre_seleccionado].iloc[0]
                st.session_state.usuario = {
                    'Nombre': usuario_data['Nombre'],
                    'Rol': usuario_data['Rol'],
                    'Nivel de Acceso': usuario_data['Nivel de Acceso']
                }
                st.sidebar.success(f"Bienvenido, {usuario_data['Nombre']} ({usuario_data['Rol']})")
            else:
                st.sidebar.error("Acceso denegado. Verifica tu contraseña o nombre de usuario.")
    else:
        st.sidebar.info("Por favor, selecciona tu nombre para iniciar sesión.")

# ===============================
# Función para verificar nivel de acceso (función faltante)
# ===============================
def verificar_acceso(nivel_requerido):
    niveles = {
        'Bajo': 1,
        'Medio': 2,
        'Alto': 3,
        'Super Admin': 4
    }
    if st.session_state.usuario:
        usuario_nivel = st.session_state.usuario['Nivel de Acceso']
        if niveles.get(usuario_nivel, 0) >= niveles.get(nivel_requerido, 0):
            return True
    return False

# ===============================
# Título de la Aplicación (esto es parte original del código)
# ===============================

st.title("🐻Soop MP 2.0🕶️")

# Sidebar para Inicio de Sesión
login()

# Si el usuario no está autenticado, detener la ejecución
if not st.session_state.usuario:
    st.stop()

# Aquí seguiría el resto del código de la aplicación, después de la autenticación
