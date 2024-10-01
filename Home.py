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

# ===============================
# Función de Autenticación con Autocompletado
# ===============================

def login():
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
        # Campo de contraseña (ahora opcional)
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

st.title("🐻Soop de Mundo Peluche🧸")

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

# ===============================
# Módulo Equipo
# ===============================

import streamlit as st
import pandas as pd
from PIL import Image

def modulo_equipo():
    # Verificar el nivel de acceso necesario para ver el módulo de equipo
    if not verificar_acceso('Medio'):
        st.error("No tienes permisos para acceder a esta sección.")
        st.stop()
    
    st.header("👥 Equipo de Trabajo")

    # Añadir columnas de acceso y otras si no existen
    columnas_necesarias = ['Avatar', 'Estado', 'Acceso Ventas', 'Acceso Logística', 'Acceso Administración', 'Acceso Marketing']
    
    for columna in columnas_necesarias:
        if columna not in st.session_state.df_equipo.columns:
            if columna == 'Avatar':
                st.session_state.df_equipo[columna] = 'https://via.placeholder.com/150'
            elif columna == 'Estado':
                st.session_state.df_equipo[columna] = 'Activo'
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
                        # Usar pd.concat() en lugar de .append()
                        nuevo_miembro_df = pd.DataFrame([nuevo_miembro])
                        st.session_state.df_equipo = pd.concat([st.session_state.df_equipo, nuevo_miembro_df], ignore_index=True)
                        st.success(f"Miembro {nombre} agregado exitosamente.")
                        # Guardar los cambios en Excel
                        st.session_state.df_equipo.to_excel('equipo.xlsx', index=False)
    
        st.markdown("---")
        
        # Formulario para modificar un miembro del equipo
        with st.expander("Modificar Miembro"):
            with st.form("form_modificar"):
                miembro_modificar = st.selectbox(
                    "Selecciona el nombre a modificar",
                    st.session_state.df_equipo['Nombre'].unique().tolist()
                )
                if miembro_modificar:
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
                
                if submit_modificar and miembro_modificar:
                    # Actualizar los datos del miembro
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
                    st.session_state.df_equipo.to_excel('equipo.xlsx', index=False)
    
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
                        if nombre_eliminar == st.session_state.usuario.get('Nombre', ''):
                            st.error("No puedes eliminarte a ti mismo.")
                        else:
                            st.session_state.df_equipo = st.session_state.df_equipo[st.session_state.df_equipo['Nombre'] != nombre_eliminar]
                            st.success(f"Miembro {nombre_eliminar} eliminado exitosamente.")
                            # Guardar los cambios en Excel
                            st.session_state.df_equipo.to_excel('equipo.xlsx', index=False)
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

def guardar_pedido_excel(archivo, order_data):
    """
    Función para guardar el pedido en un archivo Excel.
    Ajusta esta función según la estructura de tu archivo Excel y tus necesidades.
    """
    try:
        # Cargar el archivo existente o crear uno nuevo si no existe
        try:
            df_pedidos = pd.read_excel(archivo, sheet_name='Pedidos')
        except FileNotFoundError:
            df_pedidos = pd.DataFrame(columns=['Cliente', 'Vendedor', 'Fecha', 'Hora', 'Items'])

        # Preparar los datos del pedido
        nuevo_pedido = {
            'Cliente': order_data['cliente'],
            'Vendedor': order_data['vendedor'],
            'Fecha': order_data['fecha'],
            'Hora': order_data['hora'],
            'Items': [str(item) for item in order_data['items']]  # Convertir los ítems a string para almacenarlos
        }

        # Añadir el nuevo pedido al DataFrame existente
        df_pedidos = df_pedidos.append(nuevo_pedido, ignore_index=True)

        # Guardar de vuelta en el archivo Excel
        with pd.ExcelWriter(archivo, engine='openpyxl', mode='w') as writer:
            df_pedidos.to_excel(writer, sheet_name='Pedidos', index=False)
    except Exception as e:
        st.error(f"Error al guardar el pedido: {e}")

def modulo_ventas():
    st.header("🎐 Crear Pedido")

    # Inicializar el pedido y delete_confirm en session_state si no existen
    if 'pedido' not in st.session_state:
        st.session_state.pedido = []
    if 'delete_confirm' not in st.session_state:
        st.session_state.delete_confirm = {}

    # Colocamos el buscador de cliente y vendedor asignado en la misma fila
    col1, col2 = st.columns([2, 1])

    with col1:
        cliente_seleccionado = st.selectbox(
            "🔮 Buscar cliente", [""] + st.session_state.df_clientes['Nombre'].unique().tolist(),
            help="Escribí el nombre del cliente o seleccioná uno de la lista."
        )

    with col2:
        if cliente_seleccionado != "":  # Solo se muestran si hay cliente seleccionado
            cliente_data = st.session_state.df_clientes[st.session_state.df_clientes['Nombre'] == cliente_seleccionado].iloc[0]
            vendedores = cliente_data['Vendedores'].split(',') if pd.notna(cliente_data['Vendedores']) else ['No asignado']
            vendedor_seleccionado = st.selectbox("Vendedor asignado", vendedores, index=0)

    # Mostramos los demás campos si se selecciona un cliente distinto al espacio vacío
    if cliente_seleccionado != "":
        cliente_data = st.session_state.df_clientes[st.session_state.df_clientes['Nombre'] == cliente_seleccionado].iloc[0]

        # Mostrar descuento debajo del nombre del cliente pero arriba del vendedor asignado
        st.write(f"**Descuento:** {cliente_data['Descuento']}%")

        # Sección superior con datos: Última compra, Estado de crédito, Forma de pago
        col1, col2, col3 = st.columns(3)

        with col1:
            st.write(f"**Última compra:** {cliente_data['Fecha Modificado']}")

        with col2:
            opciones_credito = {
                'Buen pagador': '🟢',
                'Pagos regulares': '🟡',
                'Mal pagador': '🔴'
            }
            credito_cliente = cliente_data.get('Estado Credito', 'Pagos regulares')  # Asumiendo que 'Estado Credito' existe
            color_credito = opciones_credito.get(credito_cliente, '🟡')  # Valor por defecto si no coincide
            st.write(f"**Estado de crédito:** {color_credito} {credito_cliente}")

        with col3:
            forma_pago = st.selectbox(
                "💳 Forma de Pago",
                ["CC", "Contado", "Depósito/Transferencia"],
                index=["CC", "Contado", "Depósito/Transferencia"].index(cliente_data.get('Forma Pago', 'Contado'))  # Default a 'Contado'
            )

        # Desplegable para las notas del cliente
        with st.expander("🔖 Notas del Cliente"):
            st.write(cliente_data['Notas'])  # Asumiendo que hay una columna de 'Notas' en el df_clientes

        # Rubros del cliente: Ficticios en un desplegable con la opción de seleccionar y destildar
        rubros_ficticios = ["Juguetería", "Peluches", "Electrónica", "Moda", "Deportes"]  # Rubros ficticios
        rubros_seleccionados = st.multiselect("🏷️ Filtrar por Rubro del Cliente", rubros_ficticios, help="Seleccioná rubros para filtrar productos")

        # Lógica para filtrar productos por la columna 'Categorias' en lugar de 'Rubros'
        if rubros_seleccionados:
            productos_filtrados = st.session_state.df_productos[
                st.session_state.df_productos['Categorias'].apply(lambda x: any(rubro in x for rubro in rubros_seleccionados))
            ]
            productos_filtrados = productos_filtrados.sort_values(by='Fecha', ascending=False)
            cantidad_filtrados = len(productos_filtrados)
            st.info(f"Mostrando {cantidad_filtrados} productos filtrados por los rubros seleccionados")
        else:
            productos_filtrados = st.session_state.df_productos
            st.info("Mostrando todos los productos disponibles")

        # Sección de productos solo aparece si hay cliente seleccionado
        st.header("🔍 Buscador de Productos 🕶️")

        # Tres columnas: Buscador, precio, y stock con colores
        col_prod1, col_prod2, col_prod3 = st.columns([2, 1, 1])

        with col_prod1:
            # Buscador de productos con el rubro seleccionado aplicado si existe
            producto_buscado = st.selectbox(
                "Buscar producto",
                [""] + productos_filtrados['Nombre'].unique().tolist(),
                help="Escribí el nombre del producto o seleccioná uno de la lista."
            )

        if producto_buscado:
            producto_data = productos_filtrados[productos_filtrados['Nombre'] == producto_buscado].iloc[0]

            with col_prod2:
                # Mostrar precio
                st.write(f"**Precio:** ${producto_data['Precio']}")

            with col_prod3:
                # Mostrar stock con colores según la cantidad
                stock = max(0, producto_data['Stock'])  # Nos aseguramos que el stock no sea negativo
                if stock <= 0:
                    color = 'red'
                elif stock < 10:
                    color = 'orange'
                else:
                    color = 'green'

                st.markdown(f"<span style='color:{color}'>**Stock disponible:** {stock}</span>", unsafe_allow_html=True)

            # Dividimos la sección en dos columnas para mostrar el código y la cantidad en la izquierda, y la imagen a la derecha
            col_izq, col_der = st.columns([2, 1])

            with col_izq:
                # Mostrar código del producto
                st.write(f"**Código del producto:** {producto_data['Codigo']}")

                # Verificar si el campo 'forzar_multiplos' existe y es válido
                if 'forzar_multiplos' in producto_data and pd.notna(producto_data['forzar_multiplos']) and producto_data['forzar_multiplos'] > 0:
                    st.warning(f"Este producto tiene venta forzada por {int(producto_data['forzar_multiplos'])} unidades.")
                    cantidad = st.number_input(
                        "Cantidad",
                        min_value=int(producto_data['forzar_multiplos']),
                        step=int(producto_data['forzar_multiplos']),
                        key=f"cantidad_{producto_data['Codigo']}"
                    )
                else:
                    # Campo para seleccionar cantidad si no está forzada la venta por múltiplos
                    if stock > 0:
                        cantidad = st.number_input(
                            "Cantidad",
                            min_value=1,
                            max_value=stock,
                            step=1,
                            key=f"cantidad_{producto_data['Codigo']}"
                        )
                    else:
                        cantidad = 0
                        st.error("No hay stock disponible para este producto.")

                # Botón para agregar el producto al pedido, deshabilitado si no hay stock
                boton_agregar_desactivado = stock <= 0  # Deshabilitar el botón si no hay stock
                if st.button("Agregar producto", disabled=boton_agregar_desactivado, key=f"agregar_{producto_data['Codigo']}"):
                    # Verificar si el producto ya está en el pedido
                    existe = any(item['Codigo'] == producto_data['Codigo'] for item in st.session_state.pedido)
                    if existe:
                        st.warning("Este producto ya está en el pedido. Por favor, ajusta la cantidad si es necesario.")
                    else:
                        # Añadir producto al pedido con la cantidad seleccionada
                        producto_agregado = {
                            'Codigo': producto_data['Codigo'],
                            'Nombre': producto_data['Nombre'],
                            'Cantidad': cantidad,
                            'Precio': producto_data['Precio'],
                            'Importe': cantidad * producto_data['Precio']
                        }
                        st.session_state.pedido.append(producto_agregado)
                        # Descontar del stock
                        st.session_state.df_productos.loc[
                            st.session_state.df_productos['Codigo'] == producto_data['Codigo'], 'Stock'
                        ] -= cantidad
                        st.success(f"Se agregó {cantidad} unidad(es) de {producto_data['Nombre']} al pedido.")

            with col_der:
                # Mostrar imagen del producto en la columna aparte
                if pd.notna(producto_data['imagen']) and producto_data['imagen'] != '':
                    try:
                        response = requests.get(producto_data['imagen'], timeout=5)
                        response.raise_for_status()
                        image = Image.open(BytesIO(response.content))
                        st.image(image, width=200, caption="Imagen del producto")
                    except Exception as e:
                        st.write("🔗 **Imagen no disponible o URL inválida.**")

    # ----------------------------
    # Sección para mostrar el pedido actual
    # ----------------------------
    st.header("🛒 Pedido Actual")

    if st.session_state.pedido:
        # Mostrar la tabla del pedido con la opción de eliminar ítems
        for producto in st.session_state.pedido.copy():  # Use copy to avoid modification during iteration
            codigo = producto['Codigo']
            nombre = producto['Nombre']
            cantidad = producto['Cantidad']
            precio = producto['Precio']
            importe = producto['Importe']

            # Crear columnas para mostrar el producto y el botón de eliminar
            col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 1, 1, 1, 1])
            col1.write(codigo)
            col2.write(nombre)
            col3.write(cantidad)
            col4.write(f"${precio}")
            col5.write(f"${importe}")

            # Verificar si este producto está pendiente de eliminación
            if codigo in st.session_state.delete_confirm:
                # Mostrar botones "Sí" y "No"
                with col6:
                    confirmar_col = st.container()
                    col_si, col_no = confirmar_col.columns(2)
                    if col_si.button("Sí", key=f"confirmar_si_{codigo}"):
                        # Eliminar el ítem del pedido
                        index = next((i for i, item in enumerate(st.session_state.pedido) if item['Codigo'] == codigo), None)
                        if index is not None:
                            producto_eliminado = st.session_state.pedido.pop(index)
                            # Reponer el stock
                            st.session_state.df_productos.loc[
                                st.session_state.df_productos['Codigo'] == producto_eliminado['Codigo'], 'Stock'
                            ] += producto_eliminado['Cantidad']
                        # Remover del diccionario de confirmaciones
                        del st.session_state.delete_confirm[codigo]

                    if col_no.button("No", key=f"confirmar_no_{codigo}"):
                        # Cancelar la eliminación
                        del st.session_state.delete_confirm[codigo]
            else:
                # Mostrar el botón de eliminar normal
                with col6:
                    if st.button('🗑️', key=f"eliminar_{codigo}"):
                        # Marcar este ítem para eliminación
                        st.session_state.delete_confirm[codigo] = True

        # Calcular totales
        pedido_df = pd.DataFrame(st.session_state.pedido)
        total_items = pedido_df['Cantidad'].sum() if not pedido_df.empty else 0
        total_monto = pedido_df['Importe'].sum() if not pedido_df.empty else 0.0

        # Mostrar total de ítems y total del pedido en una sola fila
        col_items, col_total = st.columns([1, 1])

        with col_items:
            st.write(f"**Total de ítems:** {total_items}")

        with col_total:
            # Mostrar total del pedido al lado de total de ítems
            st.write(f"<h4 style='text-align:right;'>Total del pedido: ${total_monto:,.2f}</h4>", unsafe_allow_html=True)

        # Centrar el botón de guardar pedido
        col_guardar, _ = st.columns([2, 3])
        with col_guardar:
            if st.button("Guardar Pedido"):
                if not st.session_state.pedido:
                    st.warning("No hay ítems en el pedido para guardar.")
                else:
                    # Obtener fecha y hora actuales
                    now = datetime.now()
                    fecha_actual = now.strftime("%Y-%m-%d")
                    hora_actual = now.strftime("%H:%M:%S")

                    # Preparar datos del pedido
                    order_data = {
                        'cliente': cliente_seleccionado,
                        'vendedor': vendedor_seleccionado,
                        'fecha': fecha_actual,
                        'hora': hora_actual,
                        'items': st.session_state.pedido
                    }

                    # Guardar el pedido en la hoja 'Pedidos' de 'AdministracionSoop.xlsx'
                    guardar_pedido_excel('AdministracionSoop.xlsx', order_data)

                    # Confirmar al usuario
                    st.success("Pedido guardado exitosamente.", icon="✅")

                    # Limpiar el pedido después de guardarlo
                    st.session_state.pedido = []
                    st.session_state.delete_confirm = {}

                    # Guardar los cambios en el stock de productos
                    try:
                        st.session_state.df_productos.to_excel('archivo_modificado_productos_20240928_201237.xlsx', index=False)
                        st.success("Stock de productos actualizado correctamente.", icon="✅")
                    except Exception as e:
                        st.error(f"Error al actualizar el stock en el archivo de productos: {e}")

import streamlit as st
from streamlit.components.v1 import html

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

    # Layout de caja total con el "ojito" para ocultar/mostrar
    mostrar_caja = st.checkbox("Mostrar Caja Actual", value=True)

    col_admin, col_caja = st.columns([2, 1])

    with col_admin:
        st.subheader("💰 Administración")

    with col_caja:
        if mostrar_caja:
            # Mostrar caja en verde o rojo si es negativa
            color_caja = "red" if caja_actual < 0 else "green"
            st.write(f"<h2 style='color:{color_caja}; text-align: right;'>${caja_actual:,.2f}</h2>", unsafe_allow_html=True)

        # Mostrar último ingreso y egreso debajo de la caja
        st.write(f"**Último Ingreso:** ${monto_ultimo_ingreso:,.2f} {moneda_ultimo_ingreso}")
        st.write(f"**Último Egreso:** ${monto_ultimo_egreso:,.2f} {moneda_ultimo_egreso}")

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
# ===============================
# Módulo Estadísticas
# ===============================

def modulo_estadistica():
    st.header("📈Modulo Estadistics📊")

    # Datos ficticios (incluyendo los vendedores)
    data_ficticia_ventas = {
        'Fecha': pd.date_range(start='2024-09-01', periods=10, freq='D'),
        'Monto': [1000, 1500, 1200, 1800, 2000, 1600, 1900, 1700, 1300, 2100],
        'Vendedor': ['Joni', 'Eduardo', 'Sofi', 'Martin', 'Vasco', 'Joni', 'Eduardo', 'Sofi', 'Martin', 'Vasco']
    }
    df_ventas_ficticio = pd.DataFrame(data_ficticia_ventas)

    # Traducción manual de los días de la semana
    traduccion_dias = {
        'Monday': 'lunes',
        'Tuesday': 'martes',
        'Wednesday': 'miércoles',
        'Thursday': 'jueves',
        'Friday': 'viernes',
        'Saturday': 'sábado',
        'Sunday': 'domingo'
    }

    # Datos ficticios para productos
    productos_ficticios = {
        'Nombre': ['Peluche Oso', 'Juguete Robot', 'Auto a Control', 'Muñeca', 'Peluche León'],
        'Cantidad': [20, 15, 30, 12, 25],
        'Importe': [2000, 3000, 4500, 1800, 3000]
    }
    df_productos_ficticios = pd.DataFrame(productos_ficticios)

    # Datos ficticios para stock
    stock_ficticio = {
        'Nombre': ['Peluche Oso', 'Juguete Robot', 'Muñeca'],
        'Stock': [8, 5, 3]
    }
    df_stock_ficticio = pd.DataFrame(stock_ficticio)

    # Datos ficticios para vendedores
    vendedores_ficticios = {
        'Nombre': ['Joni', 'Eduardo', 'Sofi', 'Martin', 'Vasco'],
        'Monto': [10000, 8500, 7000, 6500, 6200]
    }
    df_vendedores_ficticio = pd.DataFrame(vendedores_ficticios)

    # Tarjetas Resumidas
    col1, col2, col3 = st.columns(3)

    # Ventas del Día (dato ficticio)
    ventas_dia_ficticia = 1800
    with col1:
        st.metric(label="Ventas del Día", value=f"${ventas_dia_ficticia:,.2f}")

    # Total de Ingresos (ficticio)
    total_ingresos_ficticio = df_ventas_ficticio['Monto'].sum()
    with col2:
        st.metric(label="Total de Ingresos", value=f"${total_ingresos_ficticio:,.2f}")

    # Total de Egresos (ficticio)
    total_egresos_ficticio = 4500  # Un dato arbitrario para mostrar
    with col3:
        st.metric(label="Total de Egresos", value=f"${total_egresos_ficticio:,.2f}")

    st.markdown("---")

    # Gráfico de ventas por día de la semana (ficticio)
    st.subheader("📅 Ventas por Día de la Semana")
    df_ventas_ficticio['Día'] = df_ventas_ficticio['Fecha'].dt.day_name().map(traduccion_dias)
    ventas_resumen_ficticio = df_ventas_ficticio.groupby('Día')['Monto'].sum().reindex(
        ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
    )
    st.bar_chart(ventas_resumen_ficticio)

    st.markdown("---")

    # Seleccionar un día y mostrar las ventas por vendedor para ese día
    st.subheader("🔍 Ventas por Día y Vendedor")
    dias_unicos = df_ventas_ficticio['Día'].unique().tolist()
    dia_seleccionado = st.selectbox("Seleccionar un día", dias_unicos)

    # Filtrar por día seleccionado
    ventas_por_dia = df_ventas_ficticio[df_ventas_ficticio['Día'] == dia_seleccionado]
    if not ventas_por_dia.empty:
        ventas_vendedores = ventas_por_dia.groupby('Vendedor')['Monto'].sum()
        st.bar_chart(ventas_vendedores)
    else:
        st.info(f"No hay datos de ventas para el día {dia_seleccionado}.")

    st.markdown("---")

    # Productos más vendidos (ficticio)
    st.subheader("🎯 Productos más Vendidos")
    st.table(df_productos_ficticios[['Nombre', 'Cantidad', 'Importe']])

    st.markdown("---")

    # Stock crítico (ficticio)
    st.subheader("⚠️ Productos con Stock Crítico")
    st.table(df_stock_ficticio[['Nombre', 'Stock']])

    st.markdown("---")

    # Productividad del equipo (ficticio)
    st.subheader("👥Productividad del Equipo📈")
    st.table(df_vendedores_ficticio[['Nombre', 'Monto']])
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
