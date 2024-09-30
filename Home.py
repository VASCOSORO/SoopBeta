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
# Inicialización del Estado de Sesión
# ===============================

# Inicializar 'pedido' si no existe
if 'pedido' not in st.session_state:
    st.session_state.pedido = []

# Inicializar 'delete_confirm' como un diccionario si no existe
if 'delete_confirm' not in st.session_state:
    st.session_state.delete_confirm = {}

# Inicializar 'usuario' en sesión si no existe
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

# Función para inicializar DataFrame desde Excel o crear uno nuevo
def inicializar_dataframe(nombre_df, columnas, archivo):
    if nombre_df not in st.session_state:
        if os.path.exists(archivo):
            try:
                df = pd.read_excel(archivo)
                # Verificar si las columnas necesarias existen
                for col in columnas:
                    if col not in df.columns:
                        df[col] = None
                df = df[columnas]
                st.session_state[nombre_df] = df
            except Exception as e:
                st.error(f"Error al cargar el archivo {archivo}: {e}")
                st.stop()
        else:
            st.warning(f"⚠️ El archivo {archivo} no existe. Creándolo automáticamente.")
            st.session_state[nombre_df] = pd.DataFrame(columns=columnas)
            try:
                st.session_state[nombre_df].to_excel(archivo, index=False)
            except Exception as e:
                st.error(f"Error al crear el archivo {archivo}: {e}")
                st.stop()

# Inicializar DataFrames necesarios
inicializar_dataframe('df_productos', ['Codigo', 'Nombre', 'Precio', 'Stock', 'forzar multiplos', 'imagen'], 'archivo_modificado_productos_20240928_201237.xlsx')
inicializar_dataframe('df_clientes', ['Nombre', 'Descuento', 'Fecha Modificado', 'Vendedores'], 'archivo_modificado_clientes_20240928_200050.xlsx')
inicializar_dataframe('df_equipo', ['Nombre', 'Rol', 'Departamento', 'Nivel de Acceso'], 'equipo.xlsx')
inicializar_dataframe('df_administracion', ['Tipo', 'Nombre', 'Detalle', 'Monto', 'Fecha', 'Hora'], 'AdministracionSoop.xlsx')

# ===============================
# Funciones de Utilidad
# ===============================

# Función para convertir DataFrame a Excel en memoria usando openpyxl
def convertir_a_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Hoja1')
    return buffer.getvalue()

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

# Función para verificar nivel de acceso
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
# Función para guardar el pedido en Excel
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

# Función para generar factura en PDF
def generar_factura(order_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Factura de Pedido", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Cliente: {order_data['cliente']}", ln=True)
    pdf.cell(200, 10, txt=f"Vendedor: {order_data['vendedor']}", ln=True)
    pdf.cell(200, 10, txt=f"Fecha: {order_data['fecha']}", ln=True)
    pdf.cell(200, 10, txt=f"Hora: {order_data['hora']}", ln=True)
    
    pdf.ln(10)  # Salto de línea
    
    # Tabla de ítems
    pdf.cell(40, 10, "Código", 1)
    pdf.cell(80, 10, "Nombre", 1)
    pdf.cell(30, 10, "Cantidad", 1)
    pdf.cell(40, 10, "Importe", 1)
    pdf.ln()
    
    for item in order_data['items']:
        pdf.cell(40, 10, item['Codigo'], 1)
        pdf.cell(80, 10, item['Nombre'], 1)
        pdf.cell(30, 10, str(item['Cantidad']), 1)
        pdf.cell(40, 10, f"${item['Importe']:.2f}", 1)
        pdf.ln()
    
    # Guardar el PDF
    pdf_output = "factura_pedido.pdf"
    pdf.output(pdf_output)
    
    # Permitir descarga
    with open(pdf_output, "rb") as f:
        st.download_button(
            label="Descargar Factura",
            data=f,
            file_name=f"Factura_Pedido_{order_data['fecha']}.pdf",
            mime="application/octet-stream"
        )
    
    # Eliminar el archivo temporal
    os.remove(pdf_output)
# ===============================
# Funciones de Cada Módulo
# ===============================

# Ventas Module
def modulo_ventas():
    st.header("📁 Ventas")
    
    # Colocamos el buscador de cliente
    col1, col2 = st.columns([2, 1])
    
    with col1:
        cliente_seleccionado = st.selectbox(
            "🔮 Buscar cliente", [""] + st.session_state.df_clientes['Nombre'].unique().tolist(),
            help="Escribí el nombre del cliente o seleccioná uno de la lista."
        )
    
    # Solo mostramos los demás campos si se selecciona un cliente distinto al espacio vacío
    if cliente_seleccionado != "":
        cliente_data = st.session_state.df_clientes[st.session_state.df_clientes['Nombre'] == cliente_seleccionado].iloc[0]
    
        # Mostrar descuento y última compra
        with col1:
            st.write(f"**Descuento:** {cliente_data['Descuento']}%")
            st.write(f"**Última compra:** {cliente_data['Fecha Modificado']}")
    
        # Mostrar vendedor principal
        with col2:
            vendedores = cliente_data['Vendedores'].split(',') if pd.notna(cliente_data['Vendedores']) else ['No asignado']
            vendedor_default = vendedores[0]
            vendedor_seleccionado = st.selectbox("Vendedor", vendedores, index=0)
            st.write(f"**Vendedor Principal:** {vendedor_seleccionado}")
    
        # Sección de productos solo aparece si hay cliente seleccionado
        st.header("📁 Buscador de Productos 🔍")
    
        # Tres columnas: Buscador, precio, y stock con colores
        col_prod1, col_prod2, col_prod3 = st.columns([2, 1, 1])
    
        with col_prod1:
            # Buscador de productos con espacio vacío al inicio
            producto_buscado = st.selectbox(
                "Buscar producto",
                [""] + st.session_state.df_productos['Nombre'].unique().tolist(),
                help="Escribí el nombre del producto o seleccioná uno de la lista."
            )
    
        if producto_buscado:
            producto_data = st.session_state.df_productos[st.session_state.df_productos['Nombre'] == producto_buscado].iloc[0]
    
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
    
                # Verificar si la venta está forzada por múltiplos
                if pd.notna(producto_data['forzar multiplos']) and producto_data['forzar multiplos'] > 0:
                    st.warning(f"Este producto tiene venta forzada por {int(producto_data['forzar multiplos'])} unidades.")
                    cantidad = st.number_input(
                        "Cantidad",
                        min_value=int(producto_data['forzar multiplos']),
                        step=int(producto_data['forzar multiplos']),
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
                else:
                    st.write("🔗 **No hay imagen disponible.**")
    
        # Mostrar el pedido actual
        if st.session_state.pedido:
            st.header("📦 Pedido actual")
    
            # Mostrar la tabla del pedido con la opción de eliminar ítems
            for idx, producto in enumerate(st.session_state.pedido.copy()):
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
                        col6.write("¿Eliminar?")
                        col_si, col_no = st.columns([1, 1])
                        with col_si:
                            if st.button("Sí", key=f"confirmar_si_{codigo}"):
                                # Eliminar el ítem del pedido
                                st.session_state.pedido.pop(idx)
                                # Reponer el stock
                                st.session_state.df_productos.loc[
                                    st.session_state.df_productos['Codigo'] == codigo, 'Stock'
                                ] += cantidad
                                # Remover del diccionario de confirmaciones
                                del st.session_state.delete_confirm[codigo]
                                st.experimental_rerun()
                        with col_no:
                            if st.button("No", key=f"confirmar_no_{codigo}"):
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
    
                        # Generar y permitir la descarga de la factura en PDF
                        generar_factura(order_data)
    
                        # Confirmar al usuario
                        st.success("Pedido guardado exitosamente.", icon="✅")
    
                        # Limpiar el pedido después de guardarlo
                        st.session_state.pedido = []
                        st.session_state.delete_confirm = {}
    
                        # Guardar los cambios en el stock de productos
                        try:
                            st.session_state.df_productos.to_excel('archivo_modificado_productos_20240928_201237.xlsx', index=False)
                        except Exception as e:
                            st.error(f"Error al actualizar el stock en el archivo de productos: {e}")
# ===============================
# Función de Autenticación con Autocompletado
# ===============================
def login():
    st.sidebar.title("🔒 Iniciar Sesión")
    
    # Selectbox con las opciones filtradas
    nombre_seleccionado = st.sidebar.selectbox(
        "Selecciona tu nombre",
        st.session_state.df_equipo['Nombre'].unique().tolist(),
        help="Logueate"
    )
    
    # Campo de texto para ingresar la contraseña (por ahora sin validar)
    if nombre_seleccionado:
        contraseña = st.sidebar.text_input("Contraseña", type="password", key="contraseña_ingresada")
        # Botón para autenticar
        if st.sidebar.button("Iniciar Sesión"):
            if contraseña == "":
                st.sidebar.error("Por favor, ingresa tu contraseña.")
            else:
                usuario_data = st.session_state.df_equipo[st.session_state.df_equipo['Nombre'] == nombre_seleccionado]
                if not usuario_data.empty:
                    usuario_data = usuario_data.iloc[0]
                    st.session_state.usuario = {
                        'Nombre': usuario_data['Nombre'],
                        'Rol': usuario_data['Rol'],
                        'Departamento': usuario_data['Departamento'],
                        'Nivel de Acceso': usuario_data['Nivel de Acceso']
                    }
                    st.sidebar.success(f"Bienvenido, {usuario_data['Nombre']} ({usuario_data['Rol']})")
                else:
                    st.sidebar.error("Nombre de usuario no encontrado.")

# ===============================
# Configuración de la Página
# ===============================
st.set_page_config(page_title="🛒 Módulo de Ventas", layout="wide")

# Título de la Aplicación
st.title("🐻 Módulo de Ventas 🛒")

# Sidebar para Inicio de Sesión
if not st.session_state.usuario:
    login()
    st.stop()

# Mostrar información del usuario en la parte superior
st.markdown(f"### Usuario: **{st.session_state.usuario['Nombre']}**")
st.markdown(f"### Rol: **{st.session_state.usuario['Rol']}**")
st.markdown("---")

# ===============================
# Navegación entre Módulos
# ===============================
st.sidebar.title("📚 Navegación")
seccion = st.sidebar.radio("Ir a", ["Ventas", "Equipo", "Administración", "Estadísticas", "Marketing", "Logística"])

# ===============================
# Implementación de Módulos
# ===============================
if seccion == "Ventas":
    modulo_ventas()
elif seccion == "Equipo":
    modulo_equipo()
elif seccion == "Administración":
    modulo_administracion()
elif seccion == "Estadísticas":
    modulo_estadistica()
elif seccion == "Marketing":
    modulo_marketing()
elif seccion == "Logística":
    modulo_logistica()

# ===============================
# Footer
# ===============================
agregar_footer()
