import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import pytz
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

# Configuración de la página
st.set_page_config(
    page_title="CRM de Productos",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Título de la aplicación
st.title("📁 CRM de Productos")

# Función para convertir DataFrame a Excel en memoria usando openpyxl
def convertir_a_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Productos')
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

# Sidebar para cargar el archivo Excel
st.sidebar.header("Cargar Archivo Excel de Productos")
uploaded_file = st.sidebar.file_uploader("📤 Subir archivo Excel", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Leer el archivo Excel
        df = pd.read_excel(uploaded_file, engine='openpyxl')

        # Mostrar los nombres de las columnas para depuración
        st.sidebar.write("🔍 **Columnas en el archivo:**")
        st.sidebar.write(df.columns.tolist())

        # Opciones de filtrado y búsqueda
        st.sidebar.header("Filtrar Productos")
        search_term = st.sidebar.text_input("Buscar por Nombre o Código")

        if search_term:
            df = df[df['Nombre'].str.contains(search_term, case=False, na=False) |
                    df['Codigo'].str.contains(search_term, case=False, na=False)]

        # Filtrado avanzado
        filtro_categoria = st.sidebar.multiselect("Selecciona Categorías", options=df['Categorias'].dropna().unique())
        filtro_activo = st.sidebar.selectbox("Estado Activo", options=['Todos', 0, 1])

        if filtro_categoria:
            df = df[df['Categorias'].str.contains('|'.join(filtro_categoria), case=False, na=False)]

        if filtro_activo != 'Todos':
            df = df[df['Activo'] == filtro_activo]

        # Configuración de la tabla AgGrid
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_side_bar()
        gb.configure_default_column(editable=True, groupable=True)
        # Especificar las columnas que se pueden editar
        columnas_editables = ['Nombre', 'Precio x Mayor', 'Costo', 'Stock', 'Descripcion', 'Categorias', 'Precio']

        for col in columnas_editables:
            gb.configure_column(col, editable=True)

        gridOptions = gb.build()

        # Mostrar la tabla editable
        st.header("📊 **Tabla de Productos:**")
        grid_response = AgGrid(
            df,
            gridOptions=gridOptions,
            data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
            update_mode=GridUpdateMode.MODEL_CHANGED,
            fit_columns_on_grid_load=True,
            theme='light',
            enable_enterprise_modules=False,
            height=500,
            reload_data=False
        )

        # Obtener el DataFrame modificado
        df_modificado = grid_response['data']

        # Botón para descargar el archivo Excel modificado
        st.header("💾 **Descargar Archivo Modificado:**")
        excel = convertir_a_excel(df_modificado)

        # Obtener la fecha y hora actual en horario de Argentina
        argentina = pytz.timezone('America/Argentina/Buenos_Aires')
        timestamp = datetime.now(argentina).strftime("%Y%m%d_%H%M%S")

        # Crear el nombre del archivo con el timestamp
        file_name = f"productos_modificados_{timestamp}.xlsx"

        st.download_button(
            label="📥 Descargar Excel Modificado",
            data=excel,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Funcionalidad para agregar un nuevo producto
        st.header("➕ **Agregar Nuevo Producto:**")
        with st.form(key='agregar_producto'):
            nuevo_id = st.text_input("Id")
            nuevo_id_externo = st.text_input("Id Externo")
            nuevo_codigo = st.text_input("Código")
            nuevo_nombre = st.text_input("Nombre")
            nuevo_precio_x_mayor = st.number_input("Precio x Mayor", min_value=0.0, step=0.01)
            nuevo_activo = st.selectbox("Activo", options=[0, 1])
            nuevo_fecha_creado = st.date_input("Fecha Creado", value=datetime.now(argentina))
            nuevo_fecha_modificado = st.date_input("Fecha Modificado", value=datetime.now(argentina))
            nuevo_descripcion = st.text_area("Descripción")
            nuevo_orden = st.number_input("Orden", min_value=0, step=1)
            nuevo_codigo_barras = st.text_input("Código de Barras")
            nuevo_unidad_bulto = st.number_input("Unidad por Bulto", min_value=0, step=1)
            nuevo_inner = st.text_input("Inner")
            nuevo_forzar_multiplos = st.text_input("Forzar Multiplos")
            nuevo_costo_usd = st.number_input("Costo usd", min_value=0.0, step=0.01)
            nuevo_costo = st.number_input("Costo", min_value=0.0, step=0.01)
            nuevo_etiquetas = st.text_input("Etiquetas")
            nuevo_stock = st.number_input("Stock", min_value=0, step=1)
            nuevo_precio_mayorista = st.number_input("Precio Mayorista", min_value=0.0, step=0.01)
            nuevo_precio_online = st.number_input("Precio Online", min_value=0.0, step=0.01)
            nuevo_precio = st.number_input("Precio", min_value=0.0, step=0.01)
            nuevo_precio_face_dolar = st.number_input("Precio Precio face Dolar", min_value=0.0, step=0.01)
            nuevo_precio_mayorista_usd = st.number_input("Precio Mayorista USD", min_value=0.0, step=0.01)
            nuevo_marca = st.text_input("Marca")
            nuevo_categorias = st.text_input("Categorias")
            nuevo_imagen = st.text_input("Imagen URL")
            nuevo_proveedor = st.text_input("Proveedor")
            nuevo_pasillo = st.text_input("Pasillo")
            nuevo_estante = st.text_input("Estante")
            nuevo_fecha_vencimiento = st.date_input("Fecha de Vencimiento", value=datetime.now(argentina))

            submit_nuevo = st.form_submit_button(label='Agregar Producto')

            if submit_nuevo:
                if not nuevo_id or not nuevo_nombre:
                    st.error("❌ Por favor, completa los campos obligatorios (Id y Nombre).")
                elif df_modificado['Id'].astype(str).str.contains(nuevo_id).any():
                    st.error("❌ El Id ya existe. Por favor, utiliza un Id único.")
                else:
                    nuevo_producto = {
                        'Id': nuevo_id,
                        'Id Externo': nuevo_id_externo,
                        'Codigo': nuevo_codigo,
                        'Nombre': nuevo_nombre,
                        'Precio x Mayor': nuevo_precio_x_mayor,
                        'Activo': nuevo_activo,
                        'Fecha Creado': nuevo_fecha_creado,
                        'Fecha Modificado': nuevo_fecha_modificado,
                        'Descripcion': nuevo_descripcion,
                        'Orden': nuevo_orden,
                        'Codigo de Barras': nuevo_codigo_barras,
                        'unidad por bulto': nuevo_unidad_bulto,
                        'inner': nuevo_inner,
                        'forzar multiplos': nuevo_forzar_multiplos,
                        'Costo usd': nuevo_costo_usd,
                        'Costo': nuevo_costo,
                        'Etiquetas': nuevo_etiquetas,
                        'Stock': nuevo_stock,
                        'Precio Mayorista': nuevo_precio_mayorista,
                        'Precio Online': nuevo_precio_online,
                        'Precio': nuevo_precio,
                        'Precio Precio face Dolar': nuevo_precio_face_dolar,
                        'Precio Mayorista USD': nuevo_precio_mayorista_usd,
                        'Marca': nuevo_marca,
                        'Categorias': nuevo_categorias,
                        'imagen': nuevo_imagen,
                        'Proveedor': nuevo_proveedor,
                        'Pasillo': nuevo_pasillo,
                        'Estante': nuevo_estante,
                        'Fecha de Vencimiento': nuevo_fecha_vencimiento
                    }
                    df_modificado = df_modificado.append(nuevo_producto, ignore_index=True)
                    st.success("✅ Producto agregado exitosamente.")

        # Funcionalidad para eliminar un producto
        st.header("🗑️ **Eliminar Producto:**")
        producto_a_eliminar = st.selectbox("Selecciona un Producto para Eliminar", df_modificado['Nombre'])

        if st.button("Eliminar Producto"):
            df_modificado = df_modificado[df_modificado['Nombre'] != producto_a_eliminar]
            st.warning(f"⚠️ Producto '{producto_a_eliminar}' eliminado.")
        
        # Funcionalidad para mostrar imágenes de productos
        st.header("🖼️ **Imágenes de Productos:**")
        for index, row in df_modificado.iterrows():
            st.subheader(row['Nombre'])
            if pd.notnull(row['imagen']) and row['imagen'] != '':
                st.image(row['imagen'], width=150)
            else:
                st.write("🔗 **No hay imagen disponible.**")

    except Exception as e:
        st.error(f"❌ Ocurrió un error al procesar el archivo: {e}")
else:
    st.info("📂 Por favor, sube un archivo Excel para comenzar.")

# Agregar el footer
agregar_footer()
