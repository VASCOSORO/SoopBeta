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
st.set_page_config(page_title="🛒 Módulo de Ventas", layout="wide")

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

# Inicializar 'df_administracion' si no existe
if 'df_administracion' not in st.session_state:
    file_path_administracion = 'AdministracionSoop.xlsx'
    if os.path.exists(file_path_administracion):
        try:
            st.session_state.df_administracion = pd.read_excel(file_path_administracion)
            # Verificar si las columnas necesarias existen
            columnas_necesarias = ['Tipo', 'Nombre', 'Detalle', 'Monto', 'Fecha', 'Hora']
            for col in columnas_necesarias:
                if col not in st.session_state.df_administracion.columns:
                    st.session_state.df_administracion[col] = None
            st.session_state.df_administracion = st.session_state.df_administracion[columnas_necesarias]
        except Exception as e:
            st.error(f"Error al cargar el archivo de administración: {e}")
            st.stop()
    else:
        st.session_state.df_administracion = pd.DataFrame(columns=['Tipo', 'Nombre', 'Detalle', 'Monto', 'Fecha', 'Hora'])

# Inicializar 'delete_confirm' como un diccionario si no existe
if 'delete_confirm' not in st.session_state:
    st.session_state.delete_confirm = {}

import streamlit as st

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
        st.sidebar.text_input("Contraseña", type="password", key="password")
        
        # Botón para iniciar sesión
        if st.sidebar.button("Iniciar Sesión"):
            usuario_data = st.session_state.df_equipo[st.session_state.df_equipo['Nombre'] == nombre_seleccionado].iloc[0]
            st.session_state.usuario = {
                'Nombre': usuario_data['Nombre'],
                'Rol': usuario_data['Rol'],
                'Nivel de Acceso': usuario_data['Nivel de Acceso']
            }
            st.sidebar.success(f"Bienvenido, {usuario_data['Nombre']} ({usuario_data['Rol']})")
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
# Función para convertir DataFrame a Excel en memoria usando openpyxl
# ===============================

def convertir_a_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Hoja1')
    return buffer.getvalue()

# ===============================
# Título de la Aplicación (esto es parte original del código)
# ===============================

st.title("🐻Soop de Mundo Peluche🕶️")

# Sidebar para Inicio de Sesión
login()

# Si el usuario no está autenticado, detener la ejecución
if not st.session_state.usuario:
    st.stop()

# Crear dos columnas con proporciones iguales
col1, col2 = st.columns(2)

with col1:
    st.write(f"**Usuario:** {st.session_state.usuario['Nombre']}")

with col2:
    st.write(f"**Rol:** {st.session_state.usuario['Rol']}")
# ===============================
# Funciones de Utilidad
# ===============================

# Función para agregar el footer
def agregar_footer():
    footer = """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        color: #555;
        text-align: center;
        padding: 10px 0;
        font-size: 14px;
    }
    </style>
    <div class="footer">
        Powered by VASCO.SORO
    </div>
    """
    st.markdown(footer, unsafe_allow_html=True)

# ===============================
# Agregar el Footer Aquí
# ===============================

agregar_footer()

# ===============================
# Función para Guardar Pedido en Excel
# ===============================

def guardar_pedido_excel(file_path, order_data):
    try:
        if os.path.exists(file_path):
            book = load_workbook(file_path)
            if 'Pedidos' in book.sheetnames:
                sheet = book['Pedidos']
            else:
                sheet = book.create_sheet('Pedidos')
                # Escribir encabezados
                sheet.append(['ID Pedido', 'Cliente', 'Vendedor', 'Fecha', 'Hora', 'Detalle', 'Monto'])
        else:
            book = Workbook()
            sheet = book.active
            sheet.title = 'Pedidos'
            sheet.append(['ID Pedido', 'Cliente', 'Vendedor', 'Fecha', 'Hora', 'Detalle', 'Monto'])
        
        # Generar ID de pedido
        if sheet.max_row == 1:
            id_pedido = 1
        else:
            last_id = sheet['A'][sheet.max_row - 1].value
            id_pedido = last_id + 1 if last_id is not None else 1
        
        # Agregar nueva fila por cada ítem
        for item in order_data['items']:
            detalle = f"{item['Nombre']} x {item['Cantidad']}"
            sheet.append([
                id_pedido,
                order_data['cliente'],
                order_data['vendedor'],
                order_data['fecha'],
                order_data['hora'],
                detalle,
                item['Importe']
            ])
        
        # Guardar el libro
        book.save(file_path)
    except Exception as e:
        st.error(f"Error al guardar el pedido: {e}")

import streamlit as st
import pandas as pd
from PIL import Image

def modulo_equipo():
    # Verificar si el DataFrame de equipo existe
    if 'df_equipo' not in st.session_state or st.session_state.df_equipo.empty:
        try:
            # Intentar cargar los datos desde el archivo Excel
            st.session_state.df_equipo = pd.read_excel('EquipoDeTrabajo.xlsx')
        except FileNotFoundError:
            st.error("No se han encontrado datos del equipo. Asegúrate de cargar los datos correctamente.")
            return
    
    # No se usará verificación de acceso por ahora

    st.header("👥 Equipo de Trabajo")

    # Añadir columnas de acceso y otras si no existen
    columnas_necesarias = ['Avatar', 'Estado', 'Acceso Ventas', 'Acceso Logística', 'Acceso Administración', 'Acceso Marketing']
    
    for columna in columnas_necesarias:
        if columna not in st.session_state.df_equipo.columns:
            if columna == 'Avatar':
                st.session_state.df_equipo['Avatar'] = 'https://via.placeholder.com/150'
            elif columna == 'Estado':
                st.session_state.df_equipo['Estado'] = 'Activo'
            else:
                st.session_state.df_equipo[columna] = False  # Valores predeterminados para accesos a módulos

    # Buscar un miembro del equipo para mostrar su ficha
    miembro_seleccionado = st.selectbox(
        "Seleccionar Miembro del Equipo", 
        [""] + st.session_state.df_equipo['Nombre'].unique().tolist()
    )

    if miembro_seleccionado:
        # Mostrar la ficha del miembro seleccionado
        miembro_data = st.session_state.df_equipo[st.session_state.df_equipo['Nombre'] == miembro_seleccionado].iloc[0]
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            # Mostrar avatar
            avatar_url = miembro_data['Avatar']
            st.image(avatar_url, width=100)
        
        with col2:
            st.subheader(miembro_data['Nombre'])
            st.write(f"**Rol:** {miembro_data['Rol']}")
            st.write(f"**Departamento:** {miembro_data['Departamento']}")
            st.write(f"**Nivel de Acceso:** {miembro_data['Nivel de Acceso']}")
            estado = "Activo" if miembro_data['Estado'] == 'Activo' else "Inactivo"
            st.write(f"**Estado:** {estado}")

        st.markdown("---")
    
    # Opciones de gestión solo para Super Admin
    if st.session_state.usuario['Nivel de Acceso'] == 'Super Admin':
        st.subheader("🔧 Gestionar Equipo")
        
        # Formulario para agregar un nuevo miembro al equipo
        with st.expander("Agregar Nuevo Miembro"):
            with st.form("form_agregar"):
                col_form1, col_form2 = st.columns(2)
                
                with col_form1:
                    nombre = st.text_input("Nombre")
                    rol = st.selectbox("Rol", [
                        'Presidente', 'Gerente General', 'Jefe de Depósito', 'Armar Pedidos',
                        'Vendedora', 'Fotógrafa y Catalogador', 'Super Admin'
                    ])
                    departamento = st.selectbox("Departamento", [
                        'Dirección', 'Depósito', 'Ventas', 'Marketing', 'Logística'
                    ])
                    nivel_acceso = st.selectbox("Nivel de Acceso", [
                        'Bajo', 'Medio', 'Alto', 'Super Admin'
                    ])
                    avatar_url = st.text_input("URL del Avatar (opcional)")
                
                with col_form2:
                    estado = st.radio("Estado del Miembro", ['Activo', 'Inactivo'], index=0)
                    # Asignación de accesos a módulos
                    acceso_ventas = st.checkbox("Acceso a Ventas")
                    acceso_logistica = st.checkbox("Acceso a Logística")
                    acceso_administracion = st.checkbox("Acceso a Administración")
                    acceso_marketing = st.checkbox("Acceso a Marketing")

                submit = st.form_submit_button("Agregar")
                
                if submit:
                    if nombre.strip() == "":
                        st.error("El nombre no puede estar vacío.")
                    elif nombre.strip() in st.session_state.df_equipo['Nombre'].values:
                        st.error("El nombre ya existe en el equipo.")
                    else:
                        nuevo_miembro = {
                            'Nombre': nombre.strip(),
                            'Rol': rol,
                            'Departamento': departamento,
                            'Nivel de Acceso': nivel_acceso,
                            'Estado': estado,
                            'Acceso Ventas': acceso_ventas,
                            'Acceso Logística': acceso_logistica,
                            'Acceso Administración': acceso_administracion,
                            'Acceso Marketing': acceso_marketing,
                            'Avatar': avatar_url if avatar_url else 'https://via.placeholder.com/150'
                        }
                        st.session_state.df_equipo = st.session_state.df_equipo.append(nuevo_miembro, ignore_index=True)
                        st.success(f"Miembro {nombre} agregado exitosamente.")
                        # Guardar los cambios en Excel
                        try:
                            st.session_state.df_equipo.to_excel('EquipoDeTrabajo.xlsx', index=False)
                        except Exception as e:
                            st.error(f"Error al guardar el archivo de equipo: {e}")
    
        st.markdown("---")
        
        # Formulario para modificar un miembro del equipo
        with st.expander("Modificar Miembro"):
            with st.form("form_modificar"):
                miembro_modificar = st.selectbox(
                    "Selecciona el nombre a modificar",
                    st.session_state.df_equipo['Nombre'].unique().tolist()
                )
                miembro_data = st.session_state.df_equipo[st.session_state.df_equipo['Nombre'] == miembro_modificar].iloc[0]
                
                col_form1, col_form2 = st.columns(2)
                
                with col_form1:
                    nombre = st.text_input("Nombre", value=miembro_data['Nombre'])
                    rol = st.selectbox("Rol", [
                        'Presidente', 'Gerente General', 'Jefe de Depósito', 'Armar Pedidos',
                        'Vendedora', 'Fotógrafa y Catalogador', 'Super Admin'
                    ], index=['Presidente', 'Gerente General', 'Jefe de Depósito', 'Armar Pedidos',
                              'Vendedora', 'Fotógrafa y Catalogador', 'Super Admin'].index(miembro_data['Rol']))
                    departamento = st.selectbox("Departamento", [
                        'Dirección', 'Depósito', 'Ventas', 'Marketing', 'Logística'
                    ], index=['Dirección', 'Depósito', 'Ventas', 'Marketing', 'Logística'].index(miembro_data['Departamento']))
                    nivel_acceso = st.selectbox("Nivel de Acceso", [
                        'Bajo', 'Medio', 'Alto', 'Super Admin'
                    ], index=['Bajo', 'Medio', 'Alto', 'Super Admin'].index(miembro_data['Nivel de Acceso']))
                    avatar_url = st.text_input("URL del Avatar", value=miembro_data['Avatar'])

                with col_form2:
                    estado = st.radio("Estado del Miembro", ['Activo', 'Inactivo'], index=0 if miembro_data['Estado'] == 'Activo' else 1)
                    # Modificar accesos a módulos
                    acceso_ventas = st.checkbox("Acceso a Ventas", value=miembro_data['Acceso Ventas'])
                    acceso_logistica = st.checkbox("Acceso a Logística", value=miembro_data['Acceso Logística'])
                    acceso_administracion = st.checkbox("Acceso a Administración", value=miembro_data['Acceso Administración'])
                    acceso_marketing = st.checkbox("Acceso a Marketing", value=miembro_data['Acceso Marketing'])

                submit_modificar = st.form_submit_button("Modificar")
                
                if submit_modificar:
                    st.session_state.df_equipo.loc[st.session_state.df_equipo['Nombre'] == miembro_modificar, 'Nombre'] = nombre
                    st.session_state.df_equipo.loc[st.session_state.df_equipo['Nombre'] == miembro_modificar, 'Rol'] = rol
                    st.session_state.df_equipo.loc[st.session_state.df_equipo['Nombre'] == miembro_modificar, 'Departamento'] = departamento
                    st.session_state.df_equipo.loc[st.session_state.df_equipo['Nombre'] == miembro_modificar, 'Nivel de Acceso'] = nivel_acceso
                    st.session_state.df_equipo.loc[st.session_state.df_equipo['Nombre'] == miembro_modificar, 'Estado'] = estado
                    st.session_state.df_equipo.loc[st.session_state.df_equipo['Nombre'] == miembro_modificar, 'Acceso Ventas'] = acceso_ventas
                    st.session_state.df_equipo.loc[st.session_state.df_equipo['Nombre'] == miembro_modificar, 'Acceso Logística'] = acceso_logistica
                    st.session_state.df_equipo.loc[st.session_state.df_equipo['Nombre'] == miembro_modificar, 'Acceso Administración'] = acceso_administracion
                    st.session_state.df_equipo.loc[st.session_state.df_equipo['Nombre'] == miembro_modificar, 'Acceso Marketing'] = acceso_marketing
                    st.session_state.df_equipo.loc[st.session_state.df_equipo['Nombre'] == miembro_modificar, 'Avatar'] = avatar_url
                    st.success(f"Miembro {miembro_modificar} modificado exitosamente.")
                    # Guardar los cambios en Excel
                    try:
                        st.session_state.df_equipo.to_excel('EquipoDeTrabajo.xlsx', index=False)
                    except Exception as e:
                        st.error(f"Error al guardar el archivo de equipo: {e}")
    
        st.markdown("---")
        
        # Formulario para eliminar un miembro del equipo
        with st.expander("Eliminar Miembro"):
            with st.form("form_eliminar"):
                nombre_eliminar = st.selectbox(
                    "Selecciona el nombre a eliminar",
                    st.session_state.df_equipo['Nombre'].unique().tolist()
                )
                submit_eliminar = st.form_submit_button("Eliminar")
                
                if submit_eliminar:
                    if nombre_eliminar in st.session_state.df_equipo['Nombre'].values:
                        if nombre_eliminar == st.session_state.usuario['Nombre']:
                            st.error("No puedes eliminarte a ti mismo.")
                        else:
                            st.session_state.df_equipo = st.session_state.df_equipo[st.session_state.df_equipo['Nombre'] != nombre_eliminar]
                            st.success(f"Miembro {nombre_eliminar} eliminado exitosamente.")
                            # Guardar los cambios en Excel
                            try:
                                st.session_state.df_equipo.to_excel('EquipoDeTrabajo.xlsx', index=False)
                            except Exception as e:
                                st.error(f"Error al guardar el archivo de equipo: {e}")
                    else:
                        st.error("El nombre seleccionado no existe.")


# ===============================
# Módulo Ventas
# ===============================

import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
from datetime import datetime
import os

def guardar_pedido_excel(archivo, order_data):
    """
    Función para guardar el pedido en un archivo Excel.
    """
    # [Function implementation remains the same]

def obtener_pedidos_cliente(cliente_nombre):
    """
    Función para obtener los pedidos anteriores de un cliente.
    """
    # [Function implementation remains the same]

def modulo_ventas():
    # CSS to adjust the spacing between the header and the button
    st.markdown("""
        <style>
        .header-button-container {
            display: flex;
            align-items: center;
        }
        .header-button-container h1 {
            margin: 0;
            padding-right: 10px;
        }
        .header-button-container button {
            margin-top: -4px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header with the '+' button immediately after 'Crear Pedido'
    st.markdown('<div class="header-button-container">', unsafe_allow_html=True)
    col1, col2 = st.columns([0.05, 0.95])
    with col1:
        st.header("🎐 Crear Pedido", anchor=False)
    with col2:
        if st.button("➕", key="btn_agregar_cliente"):
            st.session_state['mostrar_formulario_cliente'] = True
    st.markdown('</div>', unsafe_allow_html=True)

    # Ensure that there's no other '➕' button in the code
    # [Remove any previous instances of st.button("➕")]

    # Initialize session_state variables if they don't exist
    if 'pedido' not in st.session_state:
        st.session_state.pedido = []
    if 'delete_confirm' not in st.session_state:
        st.session_state.delete_confirm = {}
    if 'editar_cantidad' not in st.session_state:
        st.session_state.editar_cantidad = {}

    # Show the form to add a new client if the button is pressed
    if st.session_state.get('mostrar_formulario_cliente', False):
        # [Form implementation remains the same, ensure unique keys are used]

    # Place 'Buscar cliente' and 'Vendedor asignado' on the same line
    col_cliente, col_vendedor = st.columns(2)

    with col_cliente:
        if 'cliente_seleccionado' not in st.session_state:
            st.session_state['cliente_seleccionado'] = ''
        cliente_seleccionado = st.selectbox(
            "🔮 Buscar cliente", [""] + st.session_state.df_clientes['Nombre'].unique().tolist(),
            key='cliente_seleccionado',
            help="Escribí el nombre del cliente o seleccioná uno de la lista."
        )

    if cliente_seleccionado != "":
        # [Rest of the code remains the same, ensure unique keys are used]

        with col_vendedor:
            vendedores = st.session_state.df_equipo['Nombre'].tolist()
            vendedor_seleccionado = st.selectbox("Vendedor asignado", vendedores, index=0, key="vendedor_seleccionado")

        # [Continue with the rest of the code]

    else:
        st.info("Por favor, selecciona un cliente para continuar.")

    # [Rest of the code remains the same]

# Call the main function of the module
modulo_ventas()



   
# ===============================
# Módulo Administración
# ===============================

def modulo_administracion():
    st.header("🗃️ Administración")

    # Mostrar la caja actual en la parte superior, destacada y con último ingreso/egreso
    try:
        ingresos = st.session_state.df_administracion[st.session_state.df_administracion['Tipo'] == 'Ingreso']['Monto'].sum()
        egresos = st.session_state.df_administracion[st.session_state.df_administracion['Tipo'] == 'Egreso']['Monto'].sum()
        caja_actual = ingresos - egresos

        # Último ingreso y egreso
        ultimo_ingreso = st.session_state.df_administracion[st.session_state.df_administracion['Tipo'] == 'Ingreso'].tail(1)
        ultimo_egreso = st.session_state.df_administracion[st.session_state.df_administracion['Tipo'] == 'Egreso'].tail(1)

        # Manejo seguro de ingreso y egreso vacíos
        if not ultimo_ingreso.empty:
            monto_ultimo_ingreso = ultimo_ingreso['Monto'].values[0]
            moneda_ultimo_ingreso = "USD" if "USD" in ultimo_ingreso['Detalle'].values[0] else "ARS"
        else:
            monto_ultimo_ingreso = 0.0
            moneda_ultimo_ingreso = "ARS"

        if not ultimo_egreso.empty:
            monto_ultimo_egreso = ultimo_egreso['Monto'].values[0]
            moneda_ultimo_egreso = "USD" if "USD" in ultimo_egreso['Detalle'].values[0] else "ARS"
        else:
            monto_ultimo_egreso = 0.0
            moneda_ultimo_egreso = "ARS"
    except KeyError as e:
        st.error(f"Falta la columna {e} en el DataFrame de administración. Revisa el archivo 'AdministracionSoop.xlsx'.")
        return  # Detener la ejecución del módulo

    # Sincronizar el estado de mostrar_caja con el ícono del ojo
    if 'mostrar_caja' not in st.session_state:
        st.session_state['mostrar_caja'] = True  # Por defecto, mostrar la caja

    col_admin, col_ojo, col_caja = st.columns([2, 1, 1])

    with col_admin:
        st.subheader("💰 Administración")

    with col_ojo:
        # Usar un checkbox con el ícono del ojo para alternar la visibilidad de la caja
        mostrar_caja = st.checkbox("👁️", value=st.session_state['mostrar_caja'])
        st.session_state['mostrar_caja'] = mostrar_caja

    with col_caja:
        if st.session_state['mostrar_caja']:
            # Mostrar caja en verde o rojo si es negativa
            color_caja = "red" if caja_actual < 0 else "green"
            st.write(f"<h2 style='color:{color_caja}; text-align: right;'>${caja_actual:,.2f}</h2>", unsafe_allow_html=True)

    # Segunda fila con último ingreso y egreso
    col_admin2, col_ingreso, col_egreso = st.columns([2, 1, 1])

    with col_ingreso:
        st.write(f"<span style='color:green; text-decoration: underline;'><strong>Último Ingreso:</strong> ${monto_ultimo_ingreso:,.2f} {moneda_ultimo_ingreso}</span>", unsafe_allow_html=True)

    with col_egreso:
        st.write(f"<span style='color:red; text-decoration: underline;'><strong>Último Egreso:</strong> ${monto_ultimo_egreso:,.2f} {moneda_ultimo_egreso}</span>", unsafe_allow_html=True)

    st.markdown("---")

    # Registrar Ingreso (diseño con secciones desplegables)
    with st.expander("📥 Registrar Ingreso"):
        with st.form("form_registrar_ingreso"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                nombre_ingreso = st.text_input("Nombre del Ingreso")
            with col2:
                tipo_ingreso = st.selectbox("Tipo de Ingreso", ["Venta Cobrada", "Cobranza"])
            with col3:
                monto_ingreso = st.number_input("Monto Ingresado", min_value=0.0, step=100.0)

            col4, col5 = st.columns(2)
            with col4:
                fecha_ingreso = st.date_input("Fecha de Ingreso")
            with col5:
                hora_ingreso = st.time_input("Hora de Ingreso")

            # Cliente o cobrador según el tipo de ingreso
            if tipo_ingreso == "Venta Cobrada":
                cliente_ingreso = st.selectbox("Selecciona el Cliente", st.session_state.df_clientes['Nombre'].unique().tolist())
            else:
                cliente_ingreso = st.text_input("Nombre de quien realizó la Cobranza")

            submit_ingreso = st.form_submit_button("Registrar Ingreso")

            if submit_ingreso:
                if nombre_ingreso.strip() == "":
                    st.error("El nombre del ingreso no puede estar vacío.")
                elif monto_ingreso <= 0:
                    st.error("El monto debe ser mayor a cero.")
                else:
                    nuevo_ingreso = {
                        'Tipo': 'Ingreso',
                        'Nombre': nombre_ingreso.strip(),
                        'Detalle': f"{tipo_ingreso} - {cliente_ingreso}",
                        'Monto': monto_ingreso,
                        'Fecha': fecha_ingreso.strftime("%Y-%m-%d"),
                        'Hora': hora_ingreso.strftime("%H:%M:%S")
                    }
                    st.session_state.df_administracion = st.session_state.df_administracion.append(nuevo_ingreso, ignore_index=True)
                    st.success(f"Ingreso '{nombre_ingreso}' registrado exitosamente.")
                    st.session_state.df_administracion.to_excel('AdministracionSoop.xlsx', index=False)

    st.markdown("---")

    # Registrar Egreso (diseño con secciones desplegables)
    with st.expander("📤 Registrar Egreso"):
        with st.form("form_registrar_egreso"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                nombre_egreso = st.text_input("Nombre del Egreso")
            with col2:
                tipo_egreso = st.selectbox("Tipo de Egreso", ["Gasto", "Proveedor"])
            with col3:
                monto_egreso = st.number_input("Monto Egresado", min_value=0.0, step=100.0)

            col4, col5 = st.columns(2)
            with col4:
                fecha_egreso = st.date_input("Fecha de Egreso")
            with col5:
                hora_egreso = st.time_input("Hora de Egreso")

            if tipo_egreso == "Proveedor":
                proveedor = st.text_input("Nombre del Proveedor")
                detalle_boleta = st.text_area("Detalle de la Boleta (Item por Item)")
            else:
                proveedor = st.text_input("Destino del Gasto")
                detalle_boleta = st.text_area("Detalle del Gasto")

            submit_egreso = st.form_submit_button("Registrar Egreso")

            if submit_egreso:
                if nombre_egreso.strip() == "":
                    st.error("El nombre del egreso no puede estar vacío.")
                elif monto_egreso <= 0:
                    st.error("El monto debe ser mayor a cero.")
                elif tipo_egreso == "Proveedor" and proveedor.strip() == "":
                    st.error("El proveedor no puede estar vacío para un egreso a proveedor.")
                else:
                    detalle_completo = f"{tipo_egreso} - {proveedor} - {detalle_boleta.strip()}" if tipo_egreso == "Proveedor" else f"{tipo_egreso} - {proveedor} - {detalle_boleta.strip()}"
                    nuevo_egreso = {
                        'Tipo': 'Egreso',
                        'Nombre': nombre_egreso.strip(),
                        'Detalle': detalle_completo,
                        'Monto': monto_egreso,
                        'Fecha': fecha_egreso.strftime("%Y-%m-%d"),
                        'Hora': hora_egreso.strftime("%H:%M:%S")
                    }
                    st.session_state.df_administracion = st.session_state.df_administracion.append(nuevo_egreso, ignore_index=True)
                    st.success(f"Egreso '{nombre_egreso}' registrado exitosamente.")
                    st.session_state.df_administracion.to_excel('AdministracionSoop.xlsx', index=False)
                    
                    # Si el egreso es a un proveedor, actualizar el stock de productos
                    if tipo_egreso == "Proveedor":
                        try:
                            items = detalle_boleta.strip().split('\n')
                            for item in items:
                                if ':' in item:
                                    codigo, cantidad = item.split(':')
                                    codigo = codigo.strip()
                                    cantidad = int(cantidad.strip())
                                    if codigo in st.session_state.df_productos['Codigo'].values:
                                        st.session_state.df_productos.loc[st.session_state.df_productos['Codigo'] == codigo, 'Stock'] += cantidad
                                    else:
                                        st.warning(f"Producto con código '{codigo}' no encontrado.")
                            st.session_state.df_productos.to_excel('archivo_modificado_productos_20240928_201237.xlsx', index=False)
                            st.success("Stock de productos actualizado exitosamente.")
                        except Exception as e:
                            st.error(f"Error al actualizar el stock de productos: {e}")
import pandas as pd
import streamlit as st

import pandas as pd
import streamlit as st

# ===============================
# Módulo Estadísticas Adaptado
# ===============================
def modulo_estadistica():
    st.header("📈 Módulo Estadísticas Mejorado 📊")

    # Incluir un cargador de archivo para permitir la carga de Excel
    archivo_excel = st.file_uploader("Cargar archivo Excel", type=["xlsx"])

    if archivo_excel is not None:
        # Cargar los datos del archivo Excel subido
        df = pd.read_excel(archivo_excel)
        df['Fecha'] = pd.to_datetime(df['Fecha Creado'])

        # Agrupar ventas por vendedor y estado (envíos parciales, rechazados, etc.)
        st.subheader("📅 Segmentación de Ventas por Mes y Estado")

        # Selección de mes y año
        meses_unicos = df['Fecha'].dt.to_period('M').unique().tolist()
        mes_seleccionado = st.selectbox("Seleccionar un Mes", meses_unicos)

        # Filtrar por mes seleccionado
        df_mes_filtrado = df[df['Fecha'].dt.to_period('M') == mes_seleccionado]

        # Ventas separadas por estados: Enviadas parciales, rechazadas, completadas
        st.subheader("🔍 Segmentación por Estado de Pedido")
        estado_seleccionado = st.selectbox("Seleccionar un Estado", ['Procesado / Enviado', 'Rechazado', 'Procesado / Enviado Parcial'])

        # Filtrar los pedidos según el estado seleccionado
        df_estado_filtrado = df_mes_filtrado[df_mes_filtrado['Status'] == estado_seleccionado]

        # Gráfico de ventas por vendedor basado en estado seleccionado
        ventas_por_vendedor = df_estado_filtrado.groupby('Vendedor')['Total'].sum()
        st.bar_chart(ventas_por_vendedor)

        st.markdown("---")

        # Gráfico de ventas por vendedor en general (sin importar estado)
        st.subheader("📊 Ventas Totales por Vendedor en el Mes")
        ventas_vendedor_mes = df_mes_filtrado.groupby('Vendedor')['Total'].sum()
        st.bar_chart(ventas_vendedor_mes)

        # Productividad del equipo basado en el mes seleccionado
        st.subheader("👥 Productividad del Equipo en el Mes")
        st.table(ventas_vendedor_mes)
    else:
        st.info("Por favor, carga un archivo Excel para ver las estadísticas.")

# ===============================
# Importaciones necesarias
# ===============================
from PIL import Image, ImageDraw, ImageFont  # Para la generación de imágenes
import requests
from io import BytesIO
from fpdf import FPDF  # Para la generación de PDF

# ===============================
# Módulo Marketing
# ===============================

def modulo_marketing():
    st.header("📢Marketing y Gestión de Productos📸")

    # Parte 1: Visualizar productos
    st.subheader("🔍 Buscar y Ver Productos")
    
    col_prod1, col_prod2 = st.columns([2, 1])
    
    with col_prod1:
        producto_buscado = st.selectbox(
            "Buscar producto",
            [""] + st.session_state.df_productos['Nombre'].unique().tolist(),
            help="Escribí el nombre del producto o seleccioná uno de la lista."
        )

    if producto_buscado:
        producto_data = st.session_state.df_productos[st.session_state.df_productos['Nombre'] == producto_buscado].iloc[0]
        
        with col_prod2:
            # Mostrar stock
            st.write(f"**Stock disponible:** {producto_data['Stock']}")
        
        # Mostrar detalles del producto seleccionado
        col_detalles1, col_detalles2 = st.columns([2, 1])
        
        with col_detalles1:
            st.write(f"**Código del producto:** {producto_data['Codigo']}")
            st.write(f"**Proveedor:** {producto_data['Proveedor']}")
            
            # Verificar si la columna 'Categorías' existe en el DataFrame
            if 'Categorías' in producto_data:
                st.write(f"**Categorías:** {producto_data['Categorías']}")
            else:
                st.write("**Categorías:** No disponible")
        
        with col_detalles2:
            # Mostrar imagen del producto
            if pd.notna(producto_data['imagen']) and producto_data['imagen'] != '':
                try:
                    response = requests.get(producto_data['imagen'], timeout=5)
                    response.raise_for_status()
                    image = Image.open(BytesIO(response.content))
                    st.image(image, width=200, caption="Imagen del producto")
                except Exception as e:
                    st.write("🔗 **Imagen no disponible o URL inválida.**")
            else:
                st.write("🔗 **No hay imagen disponible.**")
    
    st.markdown("---")

    # Parte 2: Agregar nuevo producto
    st.subheader("➕ Agregar Nuevo Producto")
    
    with st.expander("Agregar Nuevo Producto", expanded=False):
        with st.form("form_agregar_producto"):
            col_form1, col_form2 = st.columns(2)
            
            with col_form1:
                codigo = st.text_input("Código del Producto")
                proveedor = st.text_input("Proveedor")
                imagen_url = st.text_input("URL de la Imagen del Producto")
                categorias = st.text_input("Categorías (separadas por coma)")
                stock = st.number_input("Stock Inicial", min_value=0)
                
            with col_form2:
                venta_forzada = st.checkbox("Venta Forzada", help="Marcar si la venta es forzada por múltiplos.")
                costo_en_pesos = st.checkbox("Agregar Precio de Costo en Pesos")
                costo_en_dolares = st.checkbox("Agregar Precio de Costo en Dólares")
                
                # Mostrar campos de precio según selección
                if costo_en_pesos:
                    precio_pesos = st.number_input("Costo en Pesos", min_value=0.0, step=0.01)
                if costo_en_dolares:
                    precio_dolares = st.number_input("Costo en Dólares", min_value=0.0, step=0.01)
            
            # Botón para agregar el producto
            agregar_producto_submit = st.form_submit_button("Agregar Producto")
            
            if agregar_producto_submit:
                nuevo_producto = {
                    'Codigo': codigo,
                    'Proveedor': proveedor,
                    'imagen': imagen_url,
                    'Categorías': categorias,
                    'Stock': stock,
                    'forzar multiplos': 1 if venta_forzada else 0,
                    'Precio Costo Pesos': precio_pesos if costo_en_pesos else None,
                    'Precio Costo USD': precio_dolares if costo_en_dolares else None
                }
                st.session_state.df_productos = st.session_state.df_productos.append(nuevo_producto, ignore_index=True)
                st.success(f"Producto {codigo} agregado exitosamente.")
                # Guardar en Excel (o en la base de datos según implementación)
                st.session_state.df_productos.to_excel('archivo_modificado_productos.xlsx', index=False)
    
    st.markdown("---")

    # Parte 3: Ver últimos productos agregados
    st.subheader("🆕Últimos Productos Agregados🔥")
    ultimos_productos = st.session_state.df_productos.tail(5)
    st.table(ultimos_productos[['Codigo', 'Nombre', 'Proveedor', 'Stock']])

    st.markdown("---")
    
    # Parte 4: Crear PDF o Imágenes
    st.subheader("🧙🏻‍♂️Crear PDF o Imagen con Productos Seleccionados📄")
    
    productos_seleccionados = st.multiselect("Seleccionar productos para el PDF/Imagen", 
                                             st.session_state.df_productos['Nombre'].unique())
    
    # Limitar selección a 6 productos
    if len(productos_seleccionados) > 6:
        st.error("Solo puedes seleccionar hasta 6 productos para el PDF o imagen.")
    elif len(productos_seleccionados) > 0:
        if st.button("Generar PDF"):
            generar_pdf(productos_seleccionados)
        if st.button("Generar Imagen PNG"):
            generar_imagen_png(productos_seleccionados)

    st.markdown("---")

    # Parte 5: Creador de Flayer
    st.subheader("🎨Creador de Flayer👻")
    
    with st.expander("Generar Flayer de Productos"):
        productos_flayer = st.multiselect("Seleccionar productos para el Flayer", 
                                          st.session_state.df_productos['Nombre'].unique())
        
        if len(productos_flayer) > 6:
            st.error("Solo puedes seleccionar hasta 6 productos.")
        elif len(productos_flayer) > 0:
            if st.button("Vista previa del Flayer"):
                generar_flayer_preview(productos_flayer)
            if st.button("Generar PDF del Flayer"):
                generar_pdf_flayer(productos_flayer)
            if st.button("Generar Imagen PNG del Flayer"):
                generar_imagen_flayer(productos_flayer)

# ===============================
# Funciones para generar PDF e Imagen
# ===============================

def generar_pdf(productos):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Definir dimensiones y posiciones para una cuadrícula de 2x3 en A4
    img_width = 90
    img_height = 90
    x_positions = [10, 110]  # 2 columnas
    y_positions = [20, 120, 220]  # 3 filas
    
    pdf.set_font("Arial", size=10)
    
    for i, producto in enumerate(productos):
        producto_data = st.session_state.df_productos[st.session_state.df_productos['Nombre'] == producto].iloc[0]
        
        # Descargar la imagen del producto
        if pd.notna(producto_data['imagen']) and producto_data['imagen'] != '':
            try:
                response = requests.get(producto_data['imagen'], timeout=5)
                response.raise_for_status()
                img = Image.open(BytesIO(response.content))
                img.save(f"producto_{i}.png")  # Guardar la imagen temporalmente
                
                # Calcular la posición en la cuadrícula
                x = x_positions[i % 2]  # Alterna entre las dos columnas
                y = y_positions[i // 2]  # Alterna entre las tres filas
                
                # Agregar imagen y texto en el PDF
                pdf.image(f"producto_{i}.png", x=x, y=y, w=img_width, h=img_height)
                pdf.set_xy(x, y + img_height + 5)  # Posicionar el texto debajo de la imagen
                pdf.cell(img_width, 10, f"Producto: {producto_data['Nombre']}", ln=True)
                pdf.cell(img_width, 10, f"Código: {producto_data['Codigo']}", ln=True)
                pdf.cell(img_width, 10, f"Proveedor: {producto_data['Proveedor']}", ln=True)
            except Exception:
                pdf.cell(img_width, 10, "No image available", ln=True)

    # Guardar el PDF en memoria
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    st.download_button(label="Descargar PDF", data=pdf_output.getvalue(), file_name="productos_seleccionados.pdf")

def generar_imagen_png(productos):
    # Crear una imagen de 2 columnas y 3 filas
    width, height = 800, 1200  # Tamaño A4 aproximado
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    # Definir posiciones
    img_width = 300
    img_height = 300
    x_positions = [50, 450]  # 2 columnas
    y_positions = [50, 450, 850]  # 3 filas
    
    for i, producto in enumerate(productos):
        producto_data = st.session_state.df_productos[st.session_state.df_productos['Nombre'] == producto].iloc[0]
        
        # Descargar la imagen del producto
        if pd.notna(producto_data['imagen']) and producto_data['imagen'] != '':
            try:
                response = requests.get(producto_data['imagen'], timeout=5)
                response.raise_for_status()
                product_img = Image.open(BytesIO(response.content)).resize((img_width, img_height))
                
                # Calcular la posición en la cuadrícula
                x = x_positions[i % 2]
                y = y_positions[i // 2]
                
                # Pegar imagen y agregar texto
                img.paste(product_img, (x, y))
                draw.text((x, y + img_height + 10), f"Producto: {producto_data['Nombre']}", font=font, fill=(0, 0, 0))
                draw.text((x, y + img_height + 30), f"Código: {producto_data['Codigo']}", font=font, fill=(0, 0, 0))
                draw.text((x, y + img_height + 50), f"Proveedor: {producto_data['Proveedor']}", font=font, fill=(0, 0, 0))
            except Exception:
                draw.text((x, y), "No image available", font=font, fill=(0, 0, 0))

    # Guardar la imagen en memoria
    img_output = BytesIO()
    img.save(img_output, format="PNG")
    img_output.seek(0)
    
    # Mostrar la imagen y permitir su descarga
    st.image(img, caption="Vista previa del flayer")
    st.download_button(label="Descargar Imagen PNG", data=img_output, file_name="productos_flayer.png", mime="image/png")

# ===============================
# Funciones para generar Flayer
# ===============================

def generar_flayer_preview(productos):
    st.write("🎞️Aquí se generará una vista previa del flayer con los productos seleccionados.")
    generar_imagen_png(productos)

def generar_pdf_flayer(productos):
    st.write("📄Aquí se generará un PDF con los productos seleccionados en formato de flayer.")
    generar_pdf(productos)

def generar_imagen_flayer(productos):
    st.write("👨‍🦼Aquí se generará una imagen PNG con los productos seleccionados en formato de flayer.")
    generar_imagen_png(productos)

# ===============================
# Módulo Logística
# ===============================

import pandas as pd
import streamlit as st

def modulo_logistica():
    st.header("🚚 Gestión de Logística")

    # Parte 1: Tabla de Pedidos Ingresados
    st.subheader("🧩Pedidos Ingresados")
    
    # Simulación de datos de pedidos ingresados
    pedidos_data = {
        'N° Seguimiento': [f"PED-{i:04d}" for i in range(1, 101)],
        'Cliente': [f"Cliente {i}" for i in range(1, 101)],
        'Vendedor': [f"Vendedor {i % 5 + 1}" for i in range(1, 101)],
        'Monto': [round(5000 + i * 50, 2) for i in range(1, 101)],
        'Estado': ['Nuevo Pedido'] * 20 + ['Esperando Pago'] * 20 + ['Pedido Pagado'] * 20 + ['Pedido en Armado'] * 20 + ['Pedido Enviado'] * 20,
        'Fecha Ingreso': pd.date_range("2024-09-01", periods=100, freq='D').strftime("%d/%m/%Y"),
        'Hora Ingreso': pd.date_range("2024-09-01 08:00", periods=100, freq='D').strftime("%H:%M")
    }
    df_pedidos = pd.DataFrame(pedidos_data)
    
    # Paginación de la tabla de pedidos
    page_size = 15
    page = st.number_input("Página", min_value=1, max_value=(len(df_pedidos) // page_size) + 1, step=1)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    # Mostrar tabla de pedidos con control para modificar el estado
    for idx in range(start_idx, end_idx):
        pedido = df_pedidos.iloc[idx]
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.write(pedido['N° Seguimiento'])
        with col2:
            st.write(pedido['Cliente'])
        with col3:
            st.write(pedido['Vendedor'])
        with col4:
            st.write(f"${pedido['Monto']:,.2f}")
        with col5:
            # Modificar estado del pedido
            nuevo_estado = st.selectbox(f"Estado del Pedido {pedido['N° Seguimiento']}", 
                                        options=['Nuevo Pedido', 'Esperando Pago', 'Pedido Pagado', 
                                                 'Pedido en Armado', 'Pedido Esperando Despacho', 'Pedido Enviado'],
                                        index=['Nuevo Pedido', 'Esperando Pago', 'Pedido Pagado', 
                                               'Pedido en Armado', 'Pedido Enviado'].index(pedido['Estado']))
            df_pedidos.at[idx, 'Estado'] = nuevo_estado
        with col6:
            st.write(f"{pedido['Fecha Ingreso']} {pedido['Hora Ingreso']}")
    
    st.markdown("---")
    
    # Parte 2: Ingresar Boletas de Proveedores
    st.subheader("🚚Ingreso de Boletas de Proveedores")
    
    with st.expander("Ingresar Nueva Boleta", expanded=False):
        with st.form("form_boleta"):
            col_boleta1, col_boleta2, col_boleta3 = st.columns(3)
            
            with col_boleta1:
                proveedor = st.text_input("Proveedor")
                fecha_boleta = st.date_input("Fecha de Boleta")
            with col_boleta2:
                codigo_producto = st.text_input("Código del Producto")
                cantidad = st.number_input("Cantidad Ingresada", min_value=0)
            with col_boleta3:
                precio_unitario = st.number_input("Precio Unitario", min_value=0.0, step=0.01)
                total = cantidad * precio_unitario
                st.write(f"Total: ${total:,.2f}")
            
            # Botón para ingresar la boleta
            submitted = st.form_submit_button("Ingresar Boleta")
            if submitted:
                st.success(f"Boleta ingresada para {proveedor}, Código Producto: {codigo_producto}, Cantidad: {cantidad}, Total: ${total:,.2f}")
    
    st.markdown("---")
    
    # Parte 3: Últimos Productos Agregados (por Marketing)
    st.subheader("🆕 Últimos Productos Agregados por Marketing (Pendientes de Completar)")
    
    # Simulación de productos agregados por marketing (que aún no están disponibles en ventas)
    productos_data = {
        'Producto': [f"Producto {i}" for i in range(1, 6)],
        'Costo Pesos': [None] * 5,
        'Costo Dólares': [None] * 5,
        'Precio Mayorista': [None] * 5,
        'Precio Venta': [None] * 5,
        'Stock': [None] * 5,
        'Proveedor': [None] * 5,
        'Pasillo': [None] * 5,
        'Estante': [None] * 5
    }
    df_productos = pd.DataFrame(productos_data)
    
    for idx, producto in df_productos.iterrows():
        st.write(f"Producto: {producto['Producto']}")
        col_prod1, col_prod2, col_prod3 = st.columns(3)
        
        with col_prod1:
            costo_pesos = st.number_input(f"Costo en Pesos ({producto['Producto']})", min_value=0.0, step=0.01, key=f"costo_pesos_{idx}")
            costo_dolares = st.number_input(f"Costo en Dólares ({producto['Producto']})", min_value=0.0, step=0.01, key=f"costo_dolares_{idx}")
        with col_prod2:
            precio_mayorista = st.number_input(f"Precio Mayorista ({producto['Producto']})", min_value=0.0, step=0.01, key=f"precio_mayorista_{idx}")
            precio_venta = st.number_input(f"Precio de Venta ({producto['Producto']})", min_value=0.0, step=0.01, key=f"precio_venta_{idx}")
        with col_prod3:
            stock = st.number_input(f"Stock Inicial ({producto['Producto']})", min_value=0)
            proveedor = st.text_input(f"Proveedor ({producto['Producto']})")
            pasillo = st.text_input(f"Pasillo ({producto['Producto']})")
            estante = st.text_input(f"Estante ({producto['Producto']})")
        
        if st.button(f"Confirmar {producto['Producto']}", key=f"confirmar_{idx}"):
            st.success(f"Producto {producto['Producto']} actualizado y disponible en ventas.")
    
    st.markdown("---")

# ===============================
# Productos Module (External Link)
# ===============================

def modulo_productos():
    st.header("🔗 Acceder al Módulo de Productos")
    st.markdown("[Abrir Módulo de Productos](https://soopbeta-kz8btpqlcn4wo434nf7kkb.streamlit.app/)", unsafe_allow_html=True)

# ===============================
# Convertidor de CSV Module (External Link)
# ===============================

def modulo_convertidor_csv():
    st.header("🔗 Acceder al Convertidor de CSV")
    st.markdown("[Abrir Convertidor de CSV](https://soopbeta-jx7y7l6efyfjwfv4vbvk3a.streamlit.app/)", unsafe_allow_html=True)

# ===============================
# Navegación entre Módulos
# ===============================

st.sidebar.title("📚Modulos🧬")

# Internal navigation
seccion = st.sidebar.radio("Ir a", ["🛒Ventas", "📣Marketing", "🚚Logística", "💲Administración", "📊Estadísticas", "👻Equipo"])

# External links
st.sidebar.markdown("---")
st.sidebar.markdown("**Módulos Externos:**")
st.sidebar.markdown("[🧞‍♂️Productos](https://soopbeta-kz8btpqlcn4wo434nf7kkb.streamlit.app/)")
st.sidebar.markdown("[🧫Convertidor de CSV](https://soopbeta-jx7y7l6efyfjwfv4vbvk3a.streamlit.app/)")

# ===============================
# Implementación de Módulos
# ===============================

if seccion == "🛒Ventas":
    modulo_ventas()
    
elif seccion == "📣Marketing":
    modulo_marketing()
    
elif seccion == "🚚Logística":
    modulo_logistica()
    
elif seccion == "💲Administración":
    modulo_administracion()
    
elif seccion == "📊Estadísticas":
    modulo_estadistica()
    
elif seccion == "👻Equipo":
    modulo_equipo()
    
# ===============================
# Opciones de Logout
# ===============================

st.sidebar.markdown("---")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.usuario = None
    st.experimental_rerun()

# ===============================
# Agregar el Footer Aquí
# ===============================

agregar_footer()
