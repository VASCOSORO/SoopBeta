import streamlit as st
import pandas as pd
from openpyxl import load_workbook, Workbook
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
import os

# ===============================
# Configuración de la Página (ESTO DEBE IR AL PRINCIPIO)
# ===============================
st.set_page_config(page_title="🛒 Módulo de Ventas", layout="wide")

# ===============================
# Inicialización del Estado de Sesión
# ===============================
if 'pedido' not in st.session_state:
    st.session_state.pedido = []

# Inicializar 'df_productos' si no existe
if 'df_productos' not in st.session_state:
    file_path_productos = 'archivo_modificado_productos.xlsx'
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
    file_path_clientes = 'archivo_modificado_clientes.xlsx'
    if os.path.exists(file_path_clientes):
        try:
            st.session_state.df_clientes = pd.read_excel(file_path_clientes)
        except Exception as e:
            st.error(f"Error al cargar el archivo de clientes: {e}")
            st.stop()
    else:
        st.warning(f"⚠️ El archivo {file_path_clientes} no existe. Por favor, súbelo desde el módulo Convertidor de CSV.")
        st.session_state.df_clientes = pd.DataFrame()  # DataFrame vacío

# ===============================
# Función de Autenticación con Autocompletado
# ===============================
def login():
    st.sidebar.title("🔒 Iniciar Sesión")

    # Selectbox con las opciones de nombres disponibles
    nombre_seleccionado = st.sidebar.selectbox(
        "Selecciona tu nombre",
        [""] + st.session_state.df_productos['Nombre'].tolist(),
        key="nombre_seleccionado",
        help="Selecciona tu nombre de la lista."
    )

    # Mostrar el botón para iniciar sesión sin requerir contraseña
    if nombre_seleccionado:
        if st.sidebar.button("Iniciar Sesión"):
            st.session_state.usuario = nombre_seleccionado
            st.sidebar.success(f"Bienvenido, {nombre_seleccionado}")

# ===============================
# Módulo Marketing
# ===============================
def modulo_marketing():
    st.header("📢 Marketing y Gestión de Productos")

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
            st.write(f"**Stock disponible:** {producto_data['Stock']}")

        # Mostrar detalles del producto seleccionado
        col_detalles1, col_detalles2 = st.columns([2, 1])

        with col_detalles1:
            st.write(f"**Código del producto:** {producto_data['Codigo']}")
            st.write(f"**Proveedor:** {producto_data['Proveedor']}")
            st.write(f"**Categorías:** {producto_data.get('Categorías', 'No disponible')}")

        with col_detalles2:
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

                if costo_en_pesos:
                    precio_pesos = st.number_input("Costo en Pesos", min_value=0.0, step=0.01)
                if costo_en_dolares:
                    precio_dolares = st.number_input("Costo en Dólares", min_value=0.0, step=0.01)

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
                st.session_state.df_productos.to_excel('archivo_modificado_productos.xlsx', index=False)

    st.markdown("---")

    # Parte 3: Creador de Flayer
    st.subheader("🎨 Creador de Flayer")

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
# Módulo Estadísticas
# ===============================

def modulo_estadistica():
    st.header("📈 Estadísticas para la toma de decisiones")

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
    st.subheader("👥 Productividad del Equipo")
    st.table(df_vendedores_ficticio[['Nombre', 'Monto']])
# ===============================
# Módulo Marketing
# ===============================

def modulo_marketing():
    st.header("📢 Marketing y Gestión de Productos")

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
    st.subheader("🆕 Últimos Productos Agregados")
    ultimos_productos = st.session_state.df_productos.tail(5)
    st.table(ultimos_productos[['Codigo', 'Nombre', 'Proveedor', 'Stock']])

    st.markdown("---")
    
    # Parte 4: Crear PDF o Imágenes
    st.subheader("📄 Crear PDF o Imagen con Productos Seleccionados")
    
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
    st.subheader("🎨 Creador de Flayer")
    
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
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from fpdf import FPDF
import streamlit as st

# ===============================
# Funciones para generar PDF e Imagen
# ===============================

def generar_pdf(productos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    for i, producto in enumerate(productos, 1):
        producto_data = st.session_state.df_productos[st.session_state.df_productos['Nombre'] == producto].iloc[0]
        pdf.cell(200, 10, txt=f"Producto {i}: {producto_data['Nombre']}", ln=True)
        pdf.cell(200, 10, txt=f"Código: {producto_data['Codigo']}", ln=True)
        pdf.cell(200, 10, txt=f"Proveedor: {producto_data['Proveedor']}", ln=True)
        pdf.cell(200, 10, txt=f"Stock: {producto_data['Stock']}", ln=True)
        pdf.cell(200, 10, txt="---", ln=True)
    
    # Guardar el PDF
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    st.download_button(label="Descargar PDF", data=pdf_output.getvalue(), file_name="productos_seleccionados.pdf")


def generar_imagen_png(productos):
    """Generar una imagen PNG con los productos seleccionados en formato de flayer"""
    # Crear una imagen en blanco con Pillow
    ancho_img = 800
    alto_img = 120 * len(productos) + 100
    img = Image.new("RGB", (ancho_img, alto_img), "white")
    draw = ImageDraw.Draw(img)

    # Definir la fuente
    font = ImageFont.load_default()
    
    y_pos = 20
    for i, producto in enumerate(productos, 1):
        producto_data = st.session_state.df_productos[st.session_state.df_productos['Nombre'] == producto].iloc[0]
        
        # Dibujar el texto en la imagen
        draw.text((20, y_pos), f"Producto {i}: {producto_data['Nombre']}", font=font, fill="black")
        draw.text((20, y_pos + 20), f"Código: {producto_data['Codigo']}", font=font, fill="black")
        draw.text((20, y_pos + 40), f"Proveedor: {producto_data['Proveedor']}", font=font, fill="black")
        draw.text((20, y_pos + 60), f"Stock: {producto_data['Stock']}", font=font, fill="black")

        # Intentar agregar la imagen del producto si existe
        if pd.notna(producto_data['imagen']) and producto_data['imagen'] != '':
            try:
                response = requests.get(producto_data['imagen'], timeout=5)
                response.raise_for_status()
                product_img = Image.open(BytesIO(response.content))
                product_img = product_img.resize((100, 100))  # Redimensionar la imagen
                img.paste(product_img, (650, y_pos))  # Pegar la imagen
            except Exception as e:
                draw.text((650, y_pos), "Imagen no disponible", font=font, fill="black")
        
        y_pos += 120

    # Mostrar vista previa
    img_output = BytesIO()
    img.save(img_output, format="PNG")
    st.image(img, caption="Vista previa del Flayer", use_column_width=True)
    
    # Botón para descargar la imagen
    st.download_button(label="Descargar Imagen PNG", data=img_output.getvalue(), file_name="flayer_productos.png")

# ===============================
# Funciones para generar Flayer
# ===============================

def generar_flayer_preview(productos):
    """Generar una vista previa del flayer con los productos seleccionados"""
    st.write("🖼️ Vista previa del flayer con los productos seleccionados.")
    generar_imagen_png(productos)

def generar_pdf_flayer(productos):
    """Generar un PDF con los productos seleccionados en formato de flayer"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    for i, producto in enumerate(productos, 1):
        producto_data = st.session_state.df_productos[st.session_state.df_productos['Nombre'] == producto].iloc[0]
        pdf.cell(200, 10, txt=f"Producto {i}: {producto_data['Nombre']}", ln=True)
        pdf.cell(200, 10, txt=f"Código: {producto_data['Codigo']}", ln=True)
        pdf.cell(200, 10, txt=f"Proveedor: {producto_data['Proveedor']}", ln=True)
        pdf.cell(200, 10, txt=f"Stock: {producto_data['Stock']}", ln=True)
        pdf.cell(200, 10, txt="---", ln=True)

        # Intentar agregar la imagen del producto si existe
        if pd.notna(producto_data['imagen']) and producto_data['imagen'] != '':
            try:
                response = requests.get(producto_data['imagen'], timeout=5)
                response.raise_for_status()
                product_img = Image.open(BytesIO(response.content))
                product_img = product_img.resize((100, 100))  # Redimensionar la imagen
                product_img_output = BytesIO()
                product_img.save(product_img_output, format="JPEG")
                pdf.image(product_img_output, x=10, y=pdf.get_y(), w=30)
                pdf.ln(40)  # Crear espacio después de la imagen
            except Exception as e:
                pdf.cell(200, 10, txt="Imagen no disponible", ln=True)
                pdf.ln(10)  # Espacio extra después del texto
    
    # Guardar el PDF
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    st.download_button(label="Descargar PDF", data=pdf_output.getvalue(), file_name="flayer_productos.pdf")

def generar_imagen_flayer(productos):
    """Generar una imagen PNG con los productos seleccionados en formato de flayer"""
    generar_imagen_png(productos)

# ===============================
# Módulo Logística
# ===============================

def modulo_logistica():
    st.header("🚚 Logística")
    st.write("Aquí puedes agregar funcionalidades de logística.")
    # Placeholder: Puedes expandir esta sección con funcionalidades específicas de logística.

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

st.sidebar.title("📚 Navegación")

# Internal navigation
seccion = st.sidebar.radio("Ir a", ["Ventas", "Equipo", "Administración", "Estadísticas", "Marketing", "Logística"])

# External links
st.sidebar.markdown("---")
st.sidebar.markdown("**Módulos Externos:**")
st.sidebar.markdown("[📁 Productos](https://soopbeta-kz8btpqlcn4wo434nf7kkb.streamlit.app/)")
st.sidebar.markdown("[📁 Convertidor de CSV](https://soopbeta-jx7y7l6efyfjwfv4vbvk3a.streamlit.app/)")

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
