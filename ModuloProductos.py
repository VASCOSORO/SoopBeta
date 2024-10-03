import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import pytz
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

# Configuración de la página
st.set_page_config(
    page_title="📁 Módulo Productos",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Título de la aplicación
st.title("📁 Módulo Productos")

# Función para convertir DataFrame a CSV en memoria
def convertir_a_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Función para convertir DataFrame a Excel en memoria usando openpyxl
def convertir_a_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Productos')
    return buffer.getvalue()

# Sidebar para cargar el archivo CSV o Excel
st.sidebar.header("Cargar Archivo CSV o Excel de Productos")
uploaded_file = st.sidebar.file_uploader("📤 Subir archivo CSV o Excel", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        st.write("📂 **Leyendo archivo...**")
        # Detectar el tipo de archivo subido y leerlo
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, encoding='ISO-8859-1', sep=None, engine='python', on_bad_lines='skip')
            st.success("✅ **Archivo CSV leído correctamente.**")
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            st.success("✅ **Archivo Excel leído correctamente.**")

        st.write("🔍 **Identificando columnas...**")
        st.write(f"📋 **Columnas identificadas:** {df.columns.tolist()}")

        # Si la columna 'Categorias' no existe, crearla vacía
        if 'Categorias' not in df.columns:
            df['Categorias'] = ''

        # Mostrar el buscador para buscar un producto para editar
        st.subheader("🔍 Buscar Producto para Editar")
        buscar_producto = st.selectbox("Buscar Producto", options=[''] + df['Nombre'].tolist())

        # Si se selecciona un producto, se mostrarán los detalles para editar
        if buscar_producto:
            producto_seleccionado = df[df['Nombre'] == buscar_producto].iloc[0]
            st.write(f"**Producto Seleccionado: {producto_seleccionado['Nombre']}**")

        # Formulario para agregar o editar productos
        st.subheader("➕ Agregar/Editar Producto")
        with st.form(key='agregar_producto_unique'):

            # Primera fila: Código, Código de Barras, Activo
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                nuevo_codigo = st.text_input("Código", value=producto_seleccionado['Código'] if buscar_producto else "")
            with col2:
                nuevo_codigo_barras = st.text_input("Código de Barras", value=producto_seleccionado['Código de Barras'] if buscar_producto else "")
            with col3:
                activo = st.checkbox("Activo", value=producto_seleccionado['Activo'] == 'Sí' if buscar_producto else False)

            # Segunda fila: Nombre
            nuevo_nombre = st.text_input("Nombre", value=producto_seleccionado['Nombre'] if buscar_producto else "", key="nombre")

            # Tercera fila: Descripción
            nuevo_descripcion = st.text_area("Descripción", value=producto_seleccionado['Descripción'] if buscar_producto else "", height=100, key="descripcion")

            # Cuarta fila: Tamaño (Alto y Ancho)
            col4, col5 = st.columns([1, 1])
            with col4:
                nuevo_alto = st.number_input("Alto", min_value=0.0, step=0.01, value=producto_seleccionado['Alto'] if buscar_producto else 0.0)
            with col5:
                nuevo_ancho = st.number_input("Ancho", min_value=0.0, step=0.01, value=producto_seleccionado['Ancho'] if buscar_producto else 0.0)

            # Categorías desplegable
            categorias = df['Categorias'].dropna().unique().tolist()
            nueva_categoria = st.multiselect("Categorías", options=categorias, default=producto_seleccionado['Categorias'].split(',') if buscar_producto else [])

            # Fila de costos y precios
            st.markdown("---")
            col6, col7, col8, col9 = st.columns([1, 1, 1, 1])
            with col6:
                nuevo_costo_pesos = st.number_input("Costo (Pesos)", min_value=0.0, step=0.01, value=producto_seleccionado['Costo (Pesos)'] if buscar_producto else 0.0)
            with col7:
                nuevo_costo_usd = st.number_input("Costo (USD)", min_value=0.0, step=0.01, value=producto_seleccionado['Costo (USD)'] if buscar_producto else 0.0)
            with col8:
                ultimo_precio_pesos = st.number_input("Último Precio (Pesos)", min_value=0.0, step=0.01, value=producto_seleccionado['Último Precio (Pesos)'] if buscar_producto else 0.0)
            with col9:
                ultimo_precio_usd = st.number_input("Último Precio (USD)", min_value=0.0, step=0.01, value=producto_seleccionado['Último Precio (USD)'] if buscar_producto else 0.0)

            # Fila para Precio y Precio x Mayor con cálculos automáticos
            st.markdown("---")
            col10, col11 = st.columns([1, 1])
            with col10:
                precio_x_mayor = st.number_input("Precio x Mayor", min_value=0.0, step=0.01, value=nuevo_costo_pesos * 1.44 if nuevo_costo_pesos else 0.0)
            with col11:
                precio_venta = st.number_input("Precio", min_value=0.0, step=0.01, value=precio_x_mayor * 1.13 if precio_x_mayor else 0.0)

            # Precio x Menor calculado automáticamente
            precio_x_menor = precio_x_mayor * 1.90
            st.write(f"**Precio x Menor (automático):** {precio_x_menor}")

            # Checkboxes para mostrar precios promocionales
            st.markdown("---")
            if st.checkbox("¿Agregar Precio Promocional?"):
                precio_promocional = st.number_input("Precio Promocional", min_value=0.0, step=0.01, value=0.0)

            # Campos adicionales: Ubicación y Nota
            st.subheader("Campos Adicionales")
            col12, col13, col14 = st.columns([1, 1, 1])
            with col12:
                pasillo = st.text_input("Pasillo", value=producto_seleccionado['Pasillo'] if buscar_producto else "")
            with col13:
                estante = st.text_input("Estante", value=producto_seleccionado['Estante'] if buscar_producto else "")
            with col14:
                columna = st.text_input("Columna", value=producto_seleccionado['Columna'] if buscar_producto else "")

            # Fecha de vencimiento y Nota 1
            fecha_vencimiento = st.date_input("Fecha de Vencimiento", value=datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')))
            nota_1 = st.text_area("Nota 1", value=producto_seleccionado['Nota 1'] if buscar_producto else "")

            # Botón para agregar o editar el producto
            submit_nuevo = st.form_submit_button(label='Guardar Producto')

            if submit_nuevo:
                st.success("✅ Producto guardado exitosamente.")

    except Exception as e:
        st.error(f"❌ Ocurrió un error al procesar el archivo: {e}")

else:
    st.info("📂 Por favor, sube un archivo CSV o Excel para comenzar.")

# Agregar el footer
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

agregar_footer()
