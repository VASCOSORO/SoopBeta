import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import pytz

# Configuración de la página
st.set_page_config(
    page_title="📁 Módulo Productos",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
                nuevo_alto = st.number_input("Alto (cm)", min_value=0, step=1, value=producto_seleccionado['Alto'] if buscar_producto else 0)
            with col5:
                nuevo_ancho = st.number_input("Ancho (cm)", min_value=0, step=1, value=producto_seleccionado['Ancho'] if buscar_producto else 0)

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
                ultimo_precio_pesos = st.text_input("Último Precio (Pesos)", value="null", disabled=True)
            with col9:
                ultimo_precio_usd = st.text_input("Último Precio (USD)", value="null", disabled=True)

            # Marcar último precio en rojo si es menor que el nuevo costo
            if nuevo_costo_pesos > float(ultimo_precio_pesos) or nuevo_costo_usd > float(ultimo_precio_usd):
                col8.markdown("<p style='color:red;'>Último Precio Menor al Costo</p>", unsafe_allow_html=True)

            # Fila para Precio y Precio x Mayor con cálculos automáticos
            st.markdown("---")
            col10, col11, col12 = st.columns([1, 1, 1])
            with col10:
                precio_x_mayor = st.number_input("Precio x Mayor", min_value=0.0, step=0.01, value=nuevo_costo_pesos * 1.44 if nuevo_costo_pesos else 0.0)
            with col11:
                precio_venta = st.number_input("Precio", min_value=0.0, step=0.01, value=precio_x_mayor * 1.13 if precio_x_mayor else 0.0)
            with col12:
                precio_x_menor = st.number_input("Precio x Menor", min_value=0.0, step=0.01, value=precio_x_mayor * 1.90)

            # Checkboxes para mostrar precios promocionales
            st.markdown("---")
            if st.checkbox("¿Agregar Precio Promocional?"):
                st.write("Configura precios promocionales para cada tipo de precio.")
                col13, col14, col15 = st.columns([1, 1, 1])
                with col13:
                    precio_promocional_mayor = st.number_input("Precio Promocional x Mayor", min_value=0.0, step=0.01)
                with col14:
                    precio_promocional = st.number_input("Precio Promocional", min_value=0.0, step=0.01)
                with col15:
                    precio_promocional_menor = st.number_input("Precio Promocional x Menor", min_value=0.0, step=0.01)

            # Campos adicionales: Ubicación y Nota
            st.subheader("Campos Adicionales")
            col16, col17, col18 = st.columns([1, 1, 1])
            with col16:
                pasillo = st.text_input("Pasillo", value=producto_seleccionado['Pasillo'] if buscar_producto else "")
            with col17:
                estante = st.text_input("Estante", value=producto_seleccionado['Estante'] if buscar_producto else "")
            with col18:
                columna = st.text_input("Columna", value=producto_seleccionado['Columna'] if buscar_producto else "")

            # Fecha de vencimiento y Nota 1
            fecha_vencimiento = st.date_input("Fecha de Vencimiento", value=datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')))
            nota_1 = st.text_area("Nota 1", value=producto_seleccionado['Nota 1'] if buscar_producto else "")

            # Botón para agregar o editar el producto
            submit_nuevo = st.form_submit_button(label='Guardar Producto')

            if submit_nuevo:
                # Generar nuevo ID correlativo
                nuevo_id = df['Código'].max() + 1000 if 'Código' in df.columns else 1000
                # Crear nuevo producto
                nuevo_producto = {
                    'Código': nuevo_id,
                    'Código de Barras': nuevo_codigo_barras,
                    'Nombre': nuevo_nombre,
                    'Descripción': nuevo_descripcion,
                    'Alto': nuevo_alto,
                    'Ancho': nuevo_ancho,
                    'Categorías': ','.join(nueva_categoria),
                    'Costo (Pesos)': nuevo_costo_pesos,
                    'Costo (USD)': nuevo_costo_usd,
                    'Precio x Mayor': precio_x_mayor,
                    'Precio': precio_venta,
                    'Precio x Menor': precio_x_menor,
                    'Pasillo': pasillo,
                    'Estante': estante,
                    'Columna': columna,
                    'Fecha de Vencimiento': fecha_vencimiento,
                    'Nota 1': nota_1,
                    'Activo': 'Sí' if activo else 'No'
                }
                # Agregar al DataFrame
                df = df.append(nuevo_producto, ignore_index=True)
                st.success("✅ Producto guardado exitosamente.")

        # Descargar archivo modificado
        st.header("💾 Descargar Archivo Modificado:")
        csv = convertir_a_csv(df)
        excel = convertir_a_excel(df)

        argentina = pytz.timezone('America/Argentina/Buenos_Aires')
        timestamp = datetime.now(argentina).strftime("%Y%m%d_%H%M%S")

        # Opción para descargar como CSV
        st.download_button(
            label="📥 Descargar CSV Modificado",
            data=csv,
            file_name=f"productos_modificados_{timestamp}.csv",
            mime="text/csv"
        )

        # Opción para descargar como XLSX
        st.download_button(
            label="📥 Descargar Excel Modificado",
            data=excel,
            file_name=f"productos_modificados_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

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
