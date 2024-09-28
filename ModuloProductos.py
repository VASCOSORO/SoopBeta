import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import pytz
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
import requests
from PIL import Image

# Configuración de la página
st.set_page_config(
    page_title="📁 Modulo Productos",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Título de la aplicación
st.title("📁 Modulo Productos")

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

# Función para asegurar que el valor es al menos el mínimo permitido
def safe_value(value, min_value=0.0):
    return max(value, min_value)

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
        
        # Corregir que cada categoría sea individual en el multiselect
        categorias_separadas = set()
        for cat in df['Categorias'].dropna():
            categorias_separadas.update(cat.split(','))  # Separar por coma y agregar al conjunto

        filtro_categoria = st.sidebar.multiselect("Selecciona Categorías", options=sorted(categorias_separadas))

        # Corregir el filtro de estado activo para que sea Sí y No
        filtro_activo = st.sidebar.selectbox("Estado Activo", options=['Todos', 'Sí', 'No'])

        if filtro_categoria:
            df = df[df['Categorias'].str.contains('|'.join(filtro_categoria), case=False, na=False)]

        if filtro_activo != 'Todos':
            estado_activo = 1 if filtro_activo == 'Sí' else 0
            df = df[df['Activo'] == estado_activo]

        # Configuración de la tabla AgGrid
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_side_bar()
        gb.configure_default_column(
            editable=False,
            groupable=True,
            resizable=True,
            sortable=True,
            wrapText=True,  # Envuelve el texto para columnas largas
            autoHeight=True  # Ajusta la altura automáticamente
        )

        # Ajustar el tamaño de las columnas según el contenido
        for column in df.columns:
            gb.configure_column(column, autoWidth=True)

        gridOptions = gb.build()

        # Mostrar la tabla editable con un tema válido y mejor tamaño de columnas
        mostrar_tabla = st.checkbox("Mostrar Vista Preliminar de la Tabla", value=True)

        if mostrar_tabla:
            st.header("📊 Tabla de Productos:")
            grid_response = AgGrid(
                df,
                gridOptions=gridOptions,
                data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                update_mode=GridUpdateMode.MODEL_CHANGED,
                fit_columns_on_grid_load=True,
                theme='streamlit',  # Tema válido
                enable_enterprise_modules=False,
                height=500,
                reload_data=False
            )

            # Obtener el DataFrame modificado
            df_modificado = grid_response['data']

            # Mostrar el total de artículos filtrados
            st.write(f"Total de Artículos Filtrados: {len(df_modificado)}")

        # Seleccionar un producto
        st.header("🔍 Seleccionar Producto:")
        selected_product = st.selectbox("Selecciona un Producto", [''] + df['Nombre'].tolist())  # Opción vacía

        if selected_product:
            producto = df[df['Nombre'] == selected_product].iloc[0]

            # Mostrar los detalles del producto
            st.subheader(f"Detalles de: {selected_product}")

            # Organizar los detalles en columnas
            col1, col2 = st.columns([3, 1])

            with col1:
                # Mostrar detalles de forma no editable
                st.markdown(f"**ID:** {producto['Id']}")
                st.markdown(f"**Código:** {producto['Codigo']}")
                st.markdown(f"**Nombre:** {producto['Nombre']}")
                st.markdown(f"**Precio x Mayor:** {producto['Precio x Mayor']}")
                st.markdown(f"**Costo:** {producto['Costo']}")
                st.markdown(f"**Stock:** {producto['Stock']}")
                st.markdown(f"**Descripción:** {producto['Descripcion']}")
                st.markdown(f"**Categorías:** {producto['Categorias']}")
                st.markdown(f"**Precio:** {producto['Precio']}")

            with col2:
                # Mostrar la imagen del producto
                if pd.notnull(producto['imagen']) and producto['imagen'] != '':
                    try:
                        response = requests.get(producto['imagen'], timeout=5)
                        response.raise_for_status()
                        image = Image.open(BytesIO(response.content))
                        st.image(image, width=150)
                    except Exception as e:
                        st.write("🔗 **Imagen no disponible o URL inválida.**")
                else:
                    st.write("🔗 **No hay imagen disponible.**")

            # Opción para modificar el producto
            modificar = st.checkbox("🔄 Modificar Producto")

            if modificar:
                st.markdown("---")
                st.subheader(f"📝 Editar Detalles de: {selected_product}")

                # Mostrar un formulario con los detalles del producto para editar
                with st.form(key='editar_producto_unique'):
                    # Organizar los campos en columnas para una mejor estética
                    editar_col1, editar_col2 = st.columns([3, 1])

                    with editar_col1:
                        nuevo_nombre = st.text_input("Nombre", value=producto['Nombre'])
                        nuevo_precio_x_mayor = st.number_input(
                            "Precio x Mayor",
                            min_value=0.0,
                            step=0.01,
                            value=safe_value(float(producto['Precio x Mayor']), 0.0),
                            key='precio_x_mayor'
                        )
                        nuevo_costo = st.number_input(
                            "Costo",
                            min_value=0.0,
                            step=0.01,
                            value=safe_value(float(producto['Costo']), 0.0),
                            key='costo'
                        )
                        nuevo_stock = st.number_input(
                            "Stock",
                            min_value=0,
                            step=1,
                            value=int(safe_value(producto['Stock'], 0)),
                            key='stock'
                        )
                        nuevo_descripcion = st.text_area("Descripción", value=producto['Descripcion'], key='descripcion')
                        nuevo_categorias = st.text_input("Categorías", value=producto['Categorias'], key='categorias')
                        nuevo_precio = st.number_input(
                            "Precio",
                            min_value=0.0,
                            step=0.01,
                            value=safe_value(float(producto['Precio']), 0.0),
                            key='precio'
                        )

                    with editar_col2:
                        # Mostrar la imagen del producto
                        if pd.notnull(producto['imagen']) and producto['imagen'] != '':
                            try:
                                response = requests.get(producto['imagen'], timeout=5)
                                response.raise_for_status()
                                image = Image.open(BytesIO(response.content))
                                st.image(image, width=150)
                            except:
                                st.write("🔗 **Imagen no disponible o URL inválida.**")
                        else:
                            st.write("🔗 **No hay imagen disponible.**")

                    submit_edit = st.form_submit_button(label='Guardar Cambios')

                    if submit_edit:
                        # Validaciones
                        if not nuevo_nombre:
                            st.error("❌ El Nombre no puede estar vacío.")
                        else:
                            # Actualizar el DataFrame
                            df.loc[df['Nombre'] == selected_product, 'Nombre'] = nuevo_nombre
                            df.loc[df['Nombre'] == nuevo_nombre, 'Precio x Mayor'] = nuevo_precio_x_mayor
                            df.loc[df['Nombre'] == nuevo_nombre, 'Costo'] = nuevo_costo
                            df.loc[df['Nombre'] == nuevo_nombre, 'Stock'] = nuevo_stock
                            df.loc[df['Nombre'] == nuevo_nombre, 'Descripcion'] = nuevo_descripcion
                            df.loc[df['Nombre'] == nuevo_nombre, 'Categorias'] = nuevo_categorias
                            df.loc[df['Nombre'] == nuevo_nombre, 'Precio'] = nuevo_precio

                            st.success("✅ Producto modificado exitosamente.")

        # Botón para descargar el archivo Excel modificado
        st.header("💾 Descargar Archivo Modificado:")
        excel = convertir_a_excel(df)

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
        st.header("➕ Agregar Nuevo Producto:")
        with st.expander("Agregar Producto"):  # Cambié para que sea un expander
            with st.form(key='agregar_producto_unique'):
                nuevo_id = st.text_input("Id", key='id')
                nuevo_id_externo = st.text_input("Id Externo", key='id_externo')
                nuevo_codigo = st.text_input("Código", key='codigo')
                nuevo_nombre = st.text_input("Nombre", key='nombre')
                nuevo_precio_x_mayor = st.number_input("Precio x Mayor", min_value=0.0, step=0.01, key='nuevo_precio_x_mayor')
                nuevo_activo = st.selectbox("Activo", options=[0, 1], key='activo')
                nuevo_fecha_creado = st.date_input("Fecha Creado", value=datetime.now(argentina), key='fecha_creado')
                nuevo_fecha_modificado = st.date_input("Fecha Modificado", value=datetime.now(argentina), key='fecha_modificado')
                nuevo_descripcion = st.text_area("Descripción", key='nueva_descripcion')
                nuevo_orden = st.number_input("Orden", min_value=0, step=1, key='orden')
                nuevo_codigo_barras = st.text_input("Código de Barras", key='codigo_barras')
                nuevo_unidad_bulto = st.number_input("Unidad por Bulto", min_value=0, step=1, key='unidad_bulto')
                nuevo_inner = st.text_input("Inner", key='inner')
                nuevo_forzar_multiplos = st.text_input("Forzar Multiplos", key='forzar_multiplos')
                nuevo_costo_usd = st.number_input("Costo usd", min_value=0.0, step=0.01, key='costo_usd')
                nuevo_costo = st.number_input("Costo", min_value=0.0, step=0.01, key='nuevo_costo')
                nuevo_etiquetas = st.text_input("Etiquetas", key='etiquetas')
                nuevo_stock = st.number_input("Stock", min_value=0, step=1, key='nuevo_stock')
                nuevo_precio_mayorista = st.number_input("Precio Mayorista", min_value=0.0, step=0.01, key='precio_mayorista')
                nuevo_precio_online = st.number_input("Precio Online", min_value=0.0, step=0.01, key='precio_online')
                nuevo_precio = st.number_input("Precio", min_value=0.0, step=0.01, key='nuevo_precio')
                nuevo_precio_face_dolar = st.number_input("Precio face Dolar", min_value=0.0, step=0.01, key='precio_face_dolar')
                nuevo_precio_mayorista_usd = st.number_input("Precio Mayorista USD", min_value=0.0, step=0.01, key='precio_mayorista_usd')
                nuevo_marca = st.text_input("Marca", key='marca')
                nuevo_categorias = st.text_input("Categorias", key='nuevas_categorias')
                nuevo_imagen = st.text_input("Imagen URL", key='nueva_imagen')
                nuevo_proveedor = st.text_input("Proveedor", key='nuevo_proveedor')
                nuevo_pasillo = st.text_input("Pasillo", key='nuevo_pasillo')
                nuevo_estante = st.text_input("Estante", key='nuevo_estante')
                nuevo_fecha_vencimiento = st.date_input("Fecha de Vencimiento", value=datetime.now(argentina), key='fecha_vencimiento')

                submit_nuevo = st.form_submit_button(label='Agregar Producto')

                if submit_nuevo:
                    # Validaciones
                    if not nuevo_id or not nuevo_nombre:
                        st.error("❌ Por favor, completa los campos obligatorios (Id y Nombre).")
                    elif df['Id'].astype(str).str.contains(nuevo_id).any():
                        st.error("❌ El Id ya existe. Por favor, utiliza un Id único.")
                    else:
                        # Agregar el nuevo producto al DataFrame
                        nuevo_producto = {
                            'Id': nuevo_id,
                            'Id Externo': nuevo_id_externo,
                            'Codigo': nuevo_codigo,
                            'Nombre': nuevo_nombre,
                            'Precio': nuevo_precio,
                            'Precio x Mayor': nuevo_precio_x_mayor,
                            'Activo': nuevo_activo,
                            'Fecha Creado': nuevo_fecha_creado,
                            'Fecha Modificado',
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
                            'Precio Mayorista USD': nuevo_precio_mayorista_usd,
                            'Marca': nuevo_marca,
                            'Categorias': nuevo_categorias,
                            'imagen': nuevo_imagen,
                            'Proveedor': nuevo_proveedor,
                            'Pasillo': nuevo_pasillo,
                            'Estante': nuevo_estante,
                            'Fecha de Vencimiento': nuevo_fecha_vencimiento
                        }
                        df = df.append(nuevo_producto, ignore_index=True)
                        st.success("✅ Producto agregado exitosamente.")

    except Exception as e:
        st.error(f"❌ Ocurrió un error al procesar el archivo: {e}")
else:
    st.info("📂 Por favor, sube un archivo Excel para comenzar.")

# Agregar el footer
agregar_footer()
