# Parte 1: Imports, Inicialización del Estado de Sesión y Funciones de Utilidad

import streamlit as st
import pandas as pd
from openpyxl import load_workbook, Workbook
import json
from datetime import datetime
import pytz
import requests
from PIL import Image
from io import BytesIO
import os

# ===============================
# Inicialización del Estado de Sesión
# ===============================

# Función para inicializar DataFrames en sesión
def inicializar_dataframe(nombre_df, columnas, archivo):
    if nombre_df not in st.session_state:
        if os.path.exists(archivo):
            try:
                st.session_state[nombre_df] = pd.read_excel(archivo)
            except Exception as e:
                st.error(f"Error al cargar el archivo {archivo}: {e}")
                st.stop()
        else:
            st.warning(f"⚠️ El archivo {archivo} no existe. Creándolo automáticamente.")
            st.session_state[nombre_df] = pd.DataFrame(columns=columnas)
            st.session_state[nombre_df].to_excel(archivo, index=False)

# Inicializar DataFrames necesarios
inicializar_dataframe('df_productos', ['Codigo', 'Nombre', 'Precio', 'Stock', 'forzar multiplos', 'imagen'], 'archivo_modificado_productos_20240928_201237.xlsx')
inicializar_dataframe('df_clientes', ['Nombre', 'Descuento', 'Fecha Modificado', 'Vendedores'], 'Clientes.xlsx')
inicializar_dataframe('df_equipo', ['Nombre', 'Contraseña', 'Rol', 'Departamento', 'Nivel de Acceso', 
                                   'Número de Celular', 'Fecha de Cumpleaños', 'Dirección',
                                   'Última Vez Inició Sesión', 'Última Vez Utilizó el Sistema', 'Activo'],
                      'equipo.xlsx')
inicializar_dataframe('df_administracion', ['Tipo', 'Nombre', 'Detalle', 'Monto', 'Fecha', 'Hora'], 'AdministracionSoop.xlsx')
inicializar_dataframe('df_logistica', ['Pedido', 'Cliente', 'Vendedor', 'Monto', 'Controlado Por', 'Estado'], 'LogisticaSoop.xlsx')
inicializar_dataframe('df_picking', ['Pedido', 'Agente de Picking', 'Caja', 'Notas'], 'PickingSoop.xlsx')
inicializar_dataframe('df_estadisticas', ['Vendedor', 'Fecha', 'Monto'], 'EstadisticasSoop.xlsx')
inicializar_dataframe('df_marketing', ['Producto', 'Imagen', 'Descripción'], 'MarketingSoop.xlsx')
inicializar_dataframe('df_proveedores', ['Proveedor', 'Detalle Boleta'], 'ProveedoresSoop.xlsx')

# Inicializar 'usuario' en sesión si no existe
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

# ===============================
# Funciones de Utilidad
# ===============================

# Función para convertir DataFrame a Excel en memoria usando openpyxl
def convertir_a_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Hoja1')
    excel_bytes = buffer.getvalue()
    return excel_bytes

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

# Función para asegurar que el valor es al menos el mínimo permitido
def safe_value(value, min_value=0.0):
    return max(value, min_value)

# Función para aplicar color al stock y mostrar el título, cantidad y detalle
def color_stock(stock):
    if stock > 10:
        return f'🟢 Stock\n**{stock} unidades**\n(Suficiente stock)'
    elif stock > 0:
        return f'🟡 Stock\n**{stock} unidades**\n(Poco stock)'
    else:
        return f'🔴 Stock\n**{stock} unidades**\n(Sin stock)'

# ===============================
# Función para Guardar Pedido en Excel
# ===============================

def guardar_pedido_excel(file_path, order_data):
    try:
        if os.path.exists(file_path):
            book = load_workbook(file_path)
        else:
            book = Workbook()
        if 'Pedidos' in book.sheetnames:
            sheet = book['Pedidos']
        else:
            sheet = book.create_sheet('Pedidos')
            # Escribir encabezados
            sheet.append(['ID Pedido', 'Cliente', 'Vendedor', 'Fecha', 'Hora', 'Items'])
        
        # Generar ID de pedido
        if sheet.max_row == 1:
            id_pedido = 1
        else:
            last_id = sheet['A'][sheet.max_row - 1].value
            id_pedido = last_id + 1 if last_id is not None else 1
        
        # Formatear los ítems como JSON
        items_json = json.dumps(order_data['items'], ensure_ascii=False)
        
        # Agregar nueva fila
        sheet.append([
            id_pedido,
            order_data['cliente'],
            order_data['vendedor'],
            order_data['fecha'],
            order_data['hora'],
            items_json
        ])
        
        # Guardar el libro
        book.save(file_path)
    except Exception as e:
        st.error(f"Error al guardar el pedido: {e}")
# Parte 2: Funciones de Autenticación, Verificación de Acceso y Navegación entre Módulos

# ===============================
# Función de Autenticación con Contraseña
# ===============================

def login():
    st.sidebar.title("🔒 Iniciar Sesión")
    
    # Selectbox para seleccionar el nombre del usuario
    nombre_seleccionado = st.sidebar.selectbox(
        "Selecciona tu nombre",
        [""] + st.session_state.df_equipo['Nombre'].unique().tolist(),
        key="nombre_seleccionado",
        help="Selecciona tu nombre de la lista."
    )
    
    # Si se selecciona un nombre, mostrar campo de contraseña
    if nombre_seleccionado:
        contraseña_ingresada = st.sidebar.text_input(
            "Ingresa tu contraseña",
            type="password",
            key="contraseña_ingresada"
        )
        
        # Botón para autenticar
        if st.sidebar.button("Iniciar Sesión"):
            usuario_data = st.session_state.df_equipo[st.session_state.df_equipo['Nombre'] == nombre_seleccionado]
            if not usuario_data.empty:
                usuario_data = usuario_data.iloc[0]
                if not usuario_data['Activo']:
                    st.sidebar.error("Tu cuenta está desactivada. Contacta al administrador.")
                elif contraseña_ingresada == usuario_data['Contraseña']:
                    st.session_state.usuario = {
                        'Nombre': usuario_data['Nombre'],
                        'Rol': usuario_data['Rol'],
                        'Departamento': usuario_data['Departamento'],
                        'Nivel de Acceso': usuario_data['Nivel de Acceso']
                    }
                    st.sidebar.success(f"Bienvenido, {usuario_data['Nombre']} ({usuario_data['Rol']})")
                    
                    # Actualizar las fechas de última sesión
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.df_equipo.loc[st.session_state.df_equipo['Nombre'] == nombre_seleccionado, 'Última Vez Inició Sesión'] = now
                    st.session_state.df_equipo.loc[st.session_state.df_equipo['Nombre'] == nombre_seleccionado, 'Última Vez Utilizó el Sistema'] = now
                    st.session_state.df_equipo.to_excel('equipo.xlsx', index=False)
                else:
                    st.sidebar.error("Contraseña incorrecta. Inténtalo de nuevo.")
            else:
                st.sidebar.error("Nombre de usuario no encontrado.")
    else:
        st.sidebar.info("Por favor, selecciona tu nombre para iniciar sesión.")

# ===============================
# Función para Verificar Acceso
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
# Configuración de la Página
# ===============================

st.set_page_config(page_title="🛒 Módulo de Ventas", layout="wide")

# Título de la Aplicación
st.title("🐻 Módulo de Ventas 🛒")

# Sidebar para Inicio de Sesión
login()

# Si el usuario no está autenticado, detener la ejecución
if not st.session_state.usuario:
    st.stop()

# Mostrar información del usuario en la parte superior
st.markdown(f"### Usuario: **{st.session_state.usuario['Nombre']}**")
st.markdown(f"### Rol: **{st.session_state.usuario['Rol']}**")
st.markdown("---")

# ===============================
# Navegación entre Módulos
# ===============================

st.sidebar.title("📚 Navegación")

# Internal navigation
seccion = st.sidebar.radio("Ir a", ["Ventas", "Equipo", "Clientes", "Administración", "Estadísticas", "Marketing", "Logística"])

# External links
st.sidebar.markdown("---")
st.sidebar.markdown("**Módulos Externos:**")
st.sidebar.markdown("[📁 Productos](https://soopbeta-kz8btpqlcn4wo434nf7kkb.streamlit.app/)")
st.sidebar.markdown("[📁 Convertidor de CSV](https://soopbeta-jx7y7l6efyfjwfv4vbvk3a.streamlit.app/)")

# ===============================
# Implementación de Módulos (Parte 2 Continúa)
# ===============================

# Funciones placeholder para módulos que serán implementados en la Parte 3
def modulo_ventas():
    st.header("📁 Ventas")
    st.write("Funcionalidades de Ventas serán implementadas en la Parte 3.")

def modulo_equipo():
    st.header("👥 Equipo de Trabajo")
    st.write("Funcionalidades de Equipo serán implementadas en la Parte 3.")

def modulo_clientes():
    st.header("👥 Clientes")
    st.write("Funcionalidades de Clientes serán implementadas en la Parte 3.")

def modulo_administracion():
    st.header("⚙️ Administración")
    st.write("Funcionalidades de Administración serán implementadas en la Parte 3.")

def modulo_estadistica():
    st.header("📈 Estadísticas")
    st.write("Funcionalidades de Estadísticas serán implementadas en la Parte 3.")

def modulo_marketing():
    st.header("📢 Marketing")
    st.write("Funcionalidades de Marketing serán implementadas en la Parte 3.")

def modulo_logistica():
    st.header("🚚 Logística")
    st.write("Funcionalidades de Logística serán implementadas en la Parte 3.")

# ===============================
# Implementación de Módulos
# ===============================

if seccion == "Ventas":
    modulo_ventas()

elif seccion == "Equipo":
    modulo_equipo()

elif seccion == "Clientes":
    modulo_clientes()

elif seccion == "Administración":
    modulo_administracion()

elif seccion == "Estadísticas":
    modulo_estadistica()

elif seccion == "Marketing":
    modulo_marketing()

elif seccion == "Logística":
    modulo_logistica()

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
# Parte 3.1: Implementación del Módulo Administración

def modulo_administracion():
    st.header("⚙️ Administración")
    
    # Mostrar la caja actual
    ingresos = st.session_state.df_administracion[st.session_state.df_administracion['Tipo'] == 'Ingreso']['Monto'].sum()
    egresos = st.session_state.df_administracion[st.session_state.df_administracion['Tipo'] == 'Egreso']['Monto'].sum()
    caja_actual = ingresos - egresos
    
    st.subheader("💰 Caja Actual")
    st.write(f"**Total Ingresos/Cobrados:** ${ingresos:,.2f}")
    st.write(f"**Total Egresos/Gastos:** ${egresos:,.2f}")
    st.write(f"**Caja Disponible:** ${caja_actual:,.2f}")
    
    st.markdown("---")
    
    st.subheader("📥 Registrar Ingreso")
    with st.form("form_registrar_ingreso"):
        nombre_ingreso = st.text_input("Nombre del Ingreso")
        tipo_ingreso = st.selectbox("Tipo de Ingreso", ["Venta Cobrada", "Cobranza"])
        if tipo_ingreso == "Venta Cobrada":
            cliente_ingreso = st.selectbox("Selecciona el Cliente", st.session_state.df_clientes['Nombre'].unique().tolist())
        else:
            cliente_ingreso = st.text_input("Nombre de quien realizó la Cobranza")
        monto_ingreso = st.number_input("Monto Ingresado", min_value=0.0, step=100.0)
        fecha_ingreso = st.date_input("Fecha de Ingreso")
        hora_ingreso = st.time_input("Hora de Ingreso")
        submit_ingreso = st.form_submit_button("Registrar Ingreso")
        
        if submit_ingreso:
            if nombre_ingreso.strip() == "":
                st.error("El nombre del ingreso no puede estar vacío.")
            elif monto_ingreso <= 0:
                st.error("El monto debe ser mayor a cero.")
            else:
                detalle = f"{tipo_ingreso} - {cliente_ingreso}" if tipo_ingreso == "Venta Cobrada" else f"{tipo_ingreso} - {cliente_ingreso}"
                nuevo_ingreso = {
                    'Tipo': 'Ingreso',
                    'Nombre': nombre_ingreso.strip(),
                    'Detalle': detalle,
                    'Monto': monto_ingreso,
                    'Fecha': fecha_ingreso.strftime("%Y-%m-%d"),
                    'Hora': hora_ingreso.strftime("%H:%M:%S")
                }
                st.session_state.df_administracion = st.session_state.df_administracion.append(nuevo_ingreso, ignore_index=True)
                st.success(f"Ingreso '{nombre_ingreso}' registrado exitosamente.")
                # Guardar los cambios en Excel
                st.session_state.df_administracion.to_excel('AdministracionSoop.xlsx', index=False)
    
    st.markdown("---")
    
    st.subheader("📤 Registrar Egreso")
    with st.form("form_registrar_egreso"):
        nombre_egreso = st.text_input("Nombre del Egreso")
        tipo_egreso = st.selectbox("Tipo de Egreso", ["Gasto", "Proveedor"])
        if tipo_egreso == "Proveedor":
            proveedor = st.selectbox("Selecciona el Proveedor", st.session_state.df_proveedores['Proveedor'].unique().tolist())
            detalle_boleta = st.text_area("Detalle de la Boleta (Item por Item)")
        else:
            proveedor = st.text_input("Destino del Gasto")
            detalle_boleta = st.text_area("Detalle del Gasto")
        monto_egreso = st.number_input("Monto Egresado", min_value=0.0, step=100.0)
        fecha_egreso = st.date_input("Fecha de Egreso")
        hora_egreso = st.time_input("Hora de Egreso")
        submit_egreso = st.form_submit_button("Registrar Egreso")
        
        if submit_egreso:
            if nombre_egreso.strip() == "":
                st.error("El nombre del egreso no puede estar vacío.")
            elif monto_egreso <= 0:
                st.error("El monto debe ser mayor a cero.")
            else:
                detalle = f"{tipo_egreso} - {proveedor}"
                nuevo_egreso = {
                    'Tipo': 'Egreso',
                    'Nombre': nombre_egreso.strip(),
                    'Detalle': detalle_boleta.strip(),
                    'Monto': monto_egreso,
                    'Fecha': fecha_egreso.strftime("%Y-%m-%d"),
                    'Hora': hora_egreso.strftime("%H:%M:%S")
                }
                st.session_state.df_administracion = st.session_state.df_administracion.append(nuevo_egreso, ignore_index=True)
                st.success(f"Egreso '{nombre_egreso}' registrado exitosamente.")
                # Guardar los cambios en Excel
                st.session_state.df_administracion.to_excel('AdministracionSoop.xlsx', index=False)
                
                # Si el egreso es a un proveedor, actualizar el stock de productos
                if tipo_egreso == "Proveedor":
                    # Asumiendo que el detalle_boleta tiene productos separados por comas en el formato "Codigo:Cantidad"
                    try:
                        items = detalle_boleta.split('\n')
                        for item in items:
                            if ':' in item:
                                codigo, cantidad = item.split(':')
                                codigo = codigo.strip()
                                cantidad = int(cantidad.strip())
                                if codigo in st.session_state.df_productos['Codigo'].values:
                                    st.session_state.df_productos.loc[st.session_state.df_productos['Codigo'] == codigo, 'Stock'] += cantidad
                                else:
                                    st.warning(f"Producto con código '{codigo}' no encontrado.")
                        # Guardar los cambios en el stock de productos
                        st.session_state.df_productos.to_excel('archivo_modificado_productos_20240928_201237.xlsx', index=False)
                        st.success("Stock de productos actualizado exitosamente.")
                    except Exception as e:
                        st.error(f"Error al actualizar el stock de productos: {e}")
# Parte 3.2: Implementación del Módulo Logística

def modulo_logistica():
    st.header("🚚 Logística")
    
    # Cargar datos de logística
    inicializar_dataframe('df_logistica', ['Numero de Pedido', 'Cliente', 'Vendedor', 'Monto', 
                                          'Controlado Por', 'Estado', 'Detalles'], 'LogisticaSoop.xlsx')
    
    # Mostrar tabla de pedidos
    st.subheader("📋 Pedidos")
    st.write("Gestiona el estado de los pedidos aquí.")
    
    # Filtrar pedidos según el estado
    estados = ["Ingresado", "Esperando Pago", "Pagado", "En Proceso de Armado", 
               "Esperando Envío", "Enviado Pago", "Enviado Debe", "Rechazado"]
    estado_seleccionado = st.selectbox("Filtrar por Estado", ["Todos"] + estados)
    
    if estado_seleccionado != "Todos":
        df_filtrado = st.session_state.df_logistica[st.session_state.df_logistica['Estado'] == estado_seleccionado]
    else:
        df_filtrado = st.session_state.df_logistica.copy()
    
    # Mostrar la tabla con selección
    pedidos_seleccionados = st.selectbox("Selecciona un Pedido para ver detalles", df_filtrado['Numero de Pedido'].tolist(), key="seleccionar_pedido")
    
    if pedidos_seleccionados:
        pedido_data = st.session_state.df_logistica[st.session_state.df_logistica['Numero de Pedido'] == pedidos_seleccionados].iloc[0]
        
        st.subheader(f"Detalles del Pedido {pedidos_seleccionados}")
        st.write(f"**Cliente:** {pedido_data['Cliente']}")
        st.write(f"**Vendedor:** {pedido_data['Vendedor']}")
        st.write(f"**Monto:** ${pedido_data['Monto']:,.2f}")
        st.write(f"**Controlado Por:** {pedido_data['Controlado Por']}")
        st.write(f"**Estado Actual:** {pedido_data['Estado']}")
        
        st.markdown("---")
        
        # Formulario para actualizar el estado del pedido
        with st.form("form_actualizar_estado_logistica"):
            nuevo_estado = st.selectbox("Actualizar Estado", estados, index=estados.index(pedido_data['Estado']) if pedido_data['Estado'] in estados else 0)
            submit_estado = st.form_submit_button("Actualizar Estado")
            
            if submit_estado:
                st.session_state.df_logistica.loc[
                    st.session_state.df_logistica['Numero de Pedido'] == pedidos_seleccionados, 'Estado'
                ] = nuevo_estado
                st.success(f"Estado del pedido {pedidos_seleccionados} actualizado a '{nuevo_estado}'.")
                # Guardar los cambios en Excel
                st.session_state.df_logistica.to_excel('LogisticaSoop.xlsx', index=False)
    
    st.markdown("---")
    
    st.subheader("📝 Registrar Detalles del Pedido")
    with st.form("form_registrar_detalles_logistica"):
        numero_pedido = st.selectbox("Selecciona el Pedido", st.session_state.df_logistica['Numero de Pedido'].tolist(), key="numero_pedido_logistica")
        controlador = st.selectbox("Controlado Por", ["Johan", "Aniel", "Martin"])
        estado_nuevo = st.selectbox("Estado", estados)
        detalles = st.text_area("Detalles Adicionales")
        submit_detalles = st.form_submit_button("Registrar Detalles")
        
        if submit_detalles:
            if numero_pedido in st.session_state.df_logistica['Numero de Pedido'].values:
                st.session_state.df_logistica.loc[
                    st.session_state.df_logistica['Numero de Pedido'] == numero_pedido, 'Controlado Por'
                ] = controlador
                st.session_state.df_logistica.loc[
                    st.session_state.df_logistica['Numero de Pedido'] == numero_pedido, 'Estado'
                ] = estado_nuevo
                st.session_state.df_logistica.loc[
                    st.session_state.df_logistica['Numero de Pedido'] == numero_pedido, 'Detalles'
                ] = detalles.strip()
                st.success(f"Detalles del pedido {numero_pedido} actualizados exitosamente.")
                # Guardar los cambios en Excel
                st.session_state.df_logistica.to_excel('LogisticaSoop.xlsx', index=False)
            else:
                st.error("El número de pedido seleccionado no existe.")
# Parte 3.3: Implementación de los Módulos Picking, Estadísticas y Marketing

# ===============================
# Módulo Picking
# ===============================

def modulo_picking():
    st.header("📦 Picking")
    
    # Cargar datos de picking
    inicializar_dataframe('df_picking', ['Numero de Pedido', 'Cliente', 'Vendedor', 'Monto', 
                                        'Armado Por', 'Caja', 'Notas', 'Estado'], 'PickingSoop.xlsx')
    
    # Mostrar tabla de pedidos asignados
    st.subheader("📋 Pedidos Asignados")
    st.write("Gestiona los pedidos asignados para el armado.")
    
    # Filtrar pedidos por el usuario actual (Armadores)
    armadores = ["Martin", "Aniel", "Johan"]
    armador_actual = st.session_state.usuario['Nombre'] if st.session_state.usuario['Nombre'] in armadores else "Martin"
    
    df_asignados = st.session_state.df_picking[
        (st.session_state.df_picking['Armado Por'] == armador_actual) & 
        (st.session_state.df_picking['Estado'] == 'En Proceso de Armado')
    ]
    
    pedidos_seleccionados = st.selectbox("Selecciona un Pedido para ver detalles", df_asignados['Numero de Pedido'].tolist(), key="seleccionar_pedido_picking")
    
    if pedidos_seleccionados:
        pedido_data = st.session_state.df_picking[st.session_state.df_picking['Numero de Pedido'] == pedidos_seleccionados].iloc[0]
        
        st.subheader(f"Detalles del Pedido {pedidos_seleccionados}")
        st.write(f"**Cliente:** {pedido_data['Cliente']}")
        st.write(f"**Vendedor:** {pedido_data['Vendedor']}")
        st.write(f"**Monto:** ${pedido_data['Monto']:,.2f}")
        st.write(f"**Armado Por:** {pedido_data['Armado Por']}")
        st.write(f"**Caja:** {pedido_data['Caja']}")
        st.write(f"**Notas:** {pedido_data['Notas']}")
        st.write(f"**Estado Actual:** {pedido_data['Estado']}")
        
        st.markdown("---")
        
        # Detalles de los productos en el pedido
        st.subheader("🛒 Detalles de Productos")
        # Suponiendo que los detalles de productos están almacenados en el campo 'Detalles' como JSON
        try:
            detalles_productos = json.loads(pedido_data['Detalles'])
            df_detalles = pd.DataFrame(detalles_productos)
            st.dataframe(df_detalles, use_container_width=True)
        except:
            st.write("No hay detalles de productos disponibles.")
        
        st.markdown("---")
        
        # Formulario para actualizar detalles del pedido
        with st.form("form_actualizar_picking"):
            caja = st.text_input("Caja", value=pedido_data['Caja'])
            notas = st.text_area("Notas", value=pedido_data['Notas'])
            marcar_armado = st.checkbox("Marcar como Pedido Armado")
            submit_picking = st.form_submit_button("Actualizar Pedido")
            
            if submit_picking:
                st.session_state.df_picking.loc[
                    st.session_state.df_picking['Numero de Pedido'] == pedidos_seleccionados, 'Caja'
                ] = caja.strip()
                st.session_state.df_picking.loc[
                    st.session_state.df_picking['Numero de Pedido'] == pedidos_seleccionados, 'Notas'
                ] = notas.strip()
                if marcar_armado:
                    st.session_state.df_picking.loc[
                        st.session_state.df_picking['Numero de Pedido'] == pedidos_seleccionados, 'Estado'
                    ] = 'Pedido Armado'
                    # Actualizar el estado en Logística
                    st.session_state.df_logistica.loc[
                        st.session_state.df_logistica['Numero de Pedido'] == pedidos_seleccionados, 'Estado'
                    ] = 'Esperando Envío'
                    st.session_state.df_logistica.to_excel('LogisticaSoop.xlsx', index=False)
                    st.success(f"Pedido {pedidos_seleccionados} marcado como armado y actualizado en Logística.")
                else:
                    st.success(f"Detalles del pedido {pedidos_seleccionados} actualizados exitosamente.")
                # Guardar los cambios en Picking
                st.session_state.df_picking.to_excel('PickingSoop.xlsx', index=False)
    
    st.markdown("---")
    
    st.subheader("📝 Registrar Nuevo Pedido en Picking")
    with st.form("form_registrar_picking"):
        numero_pedido = st.selectbox("Selecciona el Pedido", st.session_state.df_logistica['Numero de Pedido'].tolist(), key="numero_pedido_picking_registrar")
        armado_por = st.selectbox("Armado Por", ["Martin", "Aniel", "Johan"])
        caja = st.text_input("Caja")
        notas = st.text_area("Notas")
        submit_picking_registrar = st.form_submit_button("Registrar en Picking")
        
        if submit_picking_registrar:
            if numero_pedido in st.session_state.df_picking['Numero de Pedido'].values:
                st.error("Este pedido ya está registrado en Picking.")
            else:
                nuevo_picking = {
                    'Numero de Pedido': numero_pedido,
                    'Cliente': st.session_state.df_logistica.loc[st.session_state.df_logistica['Numero de Pedido'] == numero_pedido, 'Cliente'].values[0],
                    'Vendedor': st.session_state.df_logistica.loc[st.session_state.df_logistica['Numero de Pedido'] == numero_pedido, 'Vendedor'].values[0],
                    'Monto': st.session_state.df_logistica.loc[st.session_state.df_logistica['Numero de Pedido'] == numero_pedido, 'Monto'].values[0],
                    'Armado Por': armado_por,
                    'Caja': caja.strip(),
                    'Notas': notas.strip(),
                    'Estado': 'En Proceso de Armado',
                    'Detalles': st.session_state.df_logistica.loc[st.session_state.df_logistica['Numero de Pedido'] == numero_pedido, 'Detalles'].values[0]
                }
                st.session_state.df_picking = st.session_state.df_picking.append(nuevo_picking, ignore_index=True)
                st.success(f"Pedido {numero_pedido} registrado en Picking exitosamente.")
                # Actualizar el estado en Logística
                st.session_state.df_logistica.loc[
                    st.session_state.df_logistica['Numero de Pedido'] == numero_pedido, 'Estado'
                ] = 'En Proceso de Armado'
                st.session_state.df_logistica.to_excel('LogisticaSoop.xlsx', index=False)
                # Guardar los cambios en Picking
                st.session_state.df_picking.to_excel('PickingSoop.xlsx', index=False)
# Parte 3.4: Implementación del Módulo Estadísticas

def modulo_estadistica():
    st.header("📈 Estadísticas")
    
    # Cargar datos de estadísticas
    inicializar_dataframe('df_estadisticas', ['Vendedor', 'Fecha', 'Monto'], 'EstadisticasSoop.xlsx')
    
    st.subheader("📊 Gráfico de Ventas por Vendedor")
    
    # Filtrar por fecha
    fecha_inicio = st.date_input("Fecha de Inicio", value=datetime(2023, 1, 1))
    fecha_fin = st.date_input("Fecha de Fin", value=datetime.now())
    
    # Filtrar por vendedor
    vendedores = ["Todos"] + st.session_state.df_estadisticas['Vendedor'].unique().tolist()
    vendedor_seleccionado = st.selectbox("Selecciona Vendedor", vendedores)
    
    # Filtrar datos
    if vendedor_seleccionado == "Todos":
        df_filtrado = st.session_state.df_estadisticas[
            (st.session_state.df_estadisticas['Fecha'] >= fecha_inicio.strftime("%Y-%m-%d")) &
            (st.session_state.df_estadisticas['Fecha'] <= fecha_fin.strftime("%Y-%m-%d"))
        ]
    else:
        df_filtrado = st.session_state.df_estadisticas[
            (st.session_state.df_estadisticas['Vendedor'] == vendedor_seleccionado) &
            (st.session_state.df_estadisticas['Fecha'] >= fecha_inicio.strftime("%Y-%m-%d")) &
            (st.session_state.df_estadisticas['Fecha'] <= fecha_fin.strftime("%Y-%m-%d"))
        ]
    
    # Agrupar datos por fecha y sumar montos
    df_ventas = df_filtrado.groupby('Fecha')['Monto'].sum().reset_index()
    
    # Mostrar gráfico
    st.line_chart(df_ventas.set_index('Fecha'))
    
    st.markdown("---")
    
    st.subheader("📊 Ventas Diarias por Vendedor")
    vendedor_detalle = st.selectbox("Selecciona Vendedor para Detalles", ["Todos"] + st.session_state.df_estadisticas['Vendedor'].unique().tolist(), key="vendedor_detalle")
    
    if vendedor_detalle == "Todos":
        df_detalle = st.session_state.df_estadisticas[
            (st.session_state.df_estadisticas['Fecha'] >= fecha_inicio.strftime("%Y-%m-%d")) &
            (st.session_state.df_estadisticas['Fecha'] <= fecha_fin.strftime("%Y-%m-%d"))
        ]
    else:
        df_detalle = st.session_state.df_estadisticas[
            (st.session_state.df_estadisticas['Vendedor'] == vendedor_detalle) &
            (st.session_state.df_estadisticas['Fecha'] >= fecha_inicio.strftime("%Y-%m-%d")) &
            (st.session_state.df_estadisticas['Fecha'] <= fecha_fin.strftime("%Y-%m-%d"))
        ]
    
    st.dataframe(df_detalle, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("📊 Estadísticas Generales")
    ventas_totales = st.session_state.df_estadisticas['Monto'].sum()
    ventas_mensuales = st.session_state.df_estadisticas.groupby(pd.to_datetime(st.session_state.df_estadisticas['Fecha']).dt.to_period("M"))['Monto'].sum()
    
    st.write(f"**Ventas Totales Hasta la Fecha:** ${ventas_totales:,.2f}")
    st.line_chart(ventas_mensuales)
    
    st.markdown("---")
    
    st.subheader("📋 Pedidos en Espera de Pago")
    # Asumiendo que hay una columna 'Estado' en Logística para filtrar
    df_espera_pago = st.session_state.df_logistica[st.session_state.df_logistica['Estado'] == 'Esperando Pago']
    st.dataframe(df_espera_pago, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("❌ Pedidos Rechazados")
    df_rechazados = st.session_state.df_logistica[st.session_state.df_logistica['Estado'] == 'Rechazado']
    st.dataframe(df_rechazados, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("🆕 Últimos 5 Pedidos Cargados")
    df_ultimos_pedidos = st.session_state.df_logistica.sort_values(by='Fecha', ascending=False).head(5)
    st.dataframe(df_ultimos_pedidos, use_container_width=True)
    
    st.subheader("📦 Últimos Pedidos Despachados")
    desplegable = st.selectbox("Selecciona para ver pedidos despachados", ["Mostrar"] + ["Últimos Pedidos Despachados"], key="desplegable_pedidos_despachados")
    if desplegable == "Mostrar":
        df_despachados = st.session_state.df_logistica[st.session_state.df_logistica['Estado'] == 'Enviado Pago']
        st.dataframe(df_despachados, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("🔍 Detalle de Boleta de Cliente")
    numero_pedido_detalle = st.selectbox("Selecciona Pedido para ver Boleta", st.session_state.df_logistica['Numero de Pedido'].tolist(), key="numero_pedido_detalle_estadisticas")
    
    if numero_pedido_detalle:
        # Suponiendo que los detalles de productos están almacenados en el campo 'Detalles' como JSON
        try:
            detalles_productos = json.loads(st.session_state.df_logistica.loc[st.session_state.df_logistica['Numero de Pedido'] == numero_pedido_detalle, 'Detalles'].values[0])
            df_boleta = pd.DataFrame(detalles_productos)
            df_boleta['Total Item'] = df_boleta['Cantidad'] * df_boleta['Precio Unitario']
            st.dataframe(df_boleta, use_container_width=True)
        except:
            st.write("No hay detalles de boleta disponibles.")
# Parte 3.4: Implementación del Módulo Marketing

def modulo_marketing():
    st.header("📢 Marketing")
    
    # Cargar datos de marketing
    inicializar_dataframe('df_marketing', ['Nombre Producto', 'Descripción', 'Imagen URL', 'Drive Link', 'Ayuda de Venta Link', 'Logística Link'], 'MarketingSoop.xlsx')
    
    st.subheader("🛍️ Gestión de Productos para Marketing")
    
    st.dataframe(st.session_state.df_marketing, use_container_width=True)
    
    st.markdown("---")
    
    # Opciones de gestión solo para Super Admin
    if st.session_state.usuario['Nivel de Acceso'] == 'Super Admin':
        st.subheader("🔧 Gestionar Productos de Marketing")
        
        # Formulario para agregar un nuevo producto
        with st.expander("Agregar Nuevo Producto de Marketing"):
            with st.form("form_agregar_producto_marketing"):
                nombre_producto = st.text_input("Nombre del Producto")
                descripcion = st.text_area("Descripción del Producto")
                imagen_url = st.text_input("URL de la Imagen")
                drive_link = st.text_input("Link a Drive")
                ayuda_venta_link = st.text_input("Link para Ayuda de Venta")
                logistica_link = st.text_input("Link para Logística")
                submit_producto = st.form_submit_button("Agregar Producto")
                
                if submit_producto:
                    if nombre_producto.strip() == "":
                        st.error("El nombre del producto no puede estar vacío.")
                    else:
                        nuevo_producto_marketing = {
                            'Nombre Producto': nombre_producto.strip(),
                            'Descripción': descripcion.strip(),
                            'Imagen URL': imagen_url.strip(),
                            'Drive Link': drive_link.strip(),
                            'Ayuda de Venta Link': ayuda_venta_link.strip(),
                            'Logística Link': logistica_link.strip()
                        }
                        st.session_state.df_marketing = st.session_state.df_marketing.append(nuevo_producto_marketing, ignore_index=True)
                        st.success(f"Producto '{nombre_producto}' agregado exitosamente.")
                        # Guardar los cambios en Excel
                        st.session_state.df_marketing.to_excel('MarketingSoop.xlsx', index=False)
        
        st.markdown("---")
        
        # Botones funcionales para cada producto
        st.subheader("🔗 Acciones Rápidas")
        for idx, producto in st.session_state.df_marketing.iterrows():
            st.write(f"### {producto['Nombre Producto']}")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Descripción:** {producto['Descripción']}")
            with col2:
                if producto['Imagen URL']:
                    try:
                        response = requests.get(producto['Imagen URL'], timeout=5)
                        response.raise_for_status()
                        image = Image.open(BytesIO(response.content))
                        st.image(image, width=150)
                    except:
                        st.write("🔗 **Imagen no disponible**")
                else:
                    st.write("🔗 **No hay imagen disponible**")
            with col3:
                st.markdown(f"[📁 Agregar al Drive]({producto['Drive Link']})" if producto['Drive Link'] else "🔗 **No disponible**")
                st.markdown(f"[📈 Crear Ayuda de Venta]({producto['Ayuda de Venta Link']})" if producto['Ayuda de Venta Link'] else "🔗 **No disponible**")
                st.markdown(f"[🚚 Pasar a Logística para Completar Ingreso]({producto['Logística Link']})" if producto['Logística Link'] else "🔗 **No disponible**")
            st.markdown("---")
# Parte 3.5: Implementación del Módulo Picking y Otros

# Nota: Esta parte ya fue incluida en Parte 3.3. Si necesitas funcionalidades adicionales específicas para Picking, asegúrate de agregarlas aquí.

# ===============================
# Módulo Estadísticas (Si no se incluyó anteriormente)
# ===============================

# Ya incluido en Parte 3.3
