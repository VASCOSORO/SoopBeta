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

        # Filtrar productos por categorías y estado activo
        st.sidebar.header("Filtrar Productos")
        
        # Separar categorías para el filtro
        df['Categorias'] = df['Categorias'].str.split(',')
        all_categories = sorted(set([cat for sublist in df['Categorias'].dropna() for cat in sublist]))

        filtro_categoria = st.sidebar.multiselect("Selecciona Categorías", options=all_categories)
        filtro_activo = st.sidebar.selectbox("Estado Activo", options=['Todos', 'Sí', 'No'])

        # Aplicar filtros
        if filtro_categoria:
            df = df[df['Categorias'].apply(lambda cats: any(cat in cats for cat in filtro_categoria))]

        if filtro_activo == 'Sí':
            df = df[df['Activo'] == 1]
        elif filtro_activo == 'No':
            df = df[df['Activo'] == 0]

        # Configuración de la tabla AgGrid
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_side_bar()
        gb.configure_default_column(editable=False, groupable=True, resizable=True, sortable=True)
        # Especificar las columnas que se pueden editar (inicialmente no editable)
        columnas_editables = ['Nombre', 'Precio x Mayor', 'Costo', 'Stock', 'Descripcion', 'Categorias', 'Precio']

        for col in columnas_editables:
            gb.configure_column(col, editable=False)

        gridOptions = gb.build()

        # Mostrar la tabla editable con un tema válido y mejor tamaño de columnas
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

        # Seleccionar un producto
        st.header("🔍 Seleccionar Producto:")
        producto_opciones = [''] + df_modificado['Nombre'].tolist()  # Valor vacío al principio
        selected_product = st.selectbox("Selecciona un Producto", producto_opciones)

        if selected_product:
            producto = df_modificado[df_modificado['Nombre'] == selected_product].iloc[0]

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
                st.markdown(f"**Categorías:** {', '.join(producto['Categorias'])}")
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
                            value=float(producto['Precio x Mayor'])
                        )
                        nuevo_costo = st.number_input(
                            "Costo",
                            min_value=0.0,
                            step=0.01,
                            value=float(producto['Costo'])
                        )
                        nuevo_stock = st.number_input(
                            "Stock",
                            min_value=0,
                            step=1,
                            value=int(producto['Stock'])
                        )
                        nuevo_descripcion = st.text_area("Descripción", value=producto['Descripcion'])
                        nuevo_categorias = st.text_input("Categorías", value=', '.join(producto['Categorias']))
                        nuevo_precio = st.number_input(
                            "Precio",
                            min_value=0.0,
                            step=0.01,
                            value=float(producto['Precio'])
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
                            df_modificado.loc[df_modificado['Nombre'] == selected_product, 'Nombre'] = nuevo_nombre
                            df_modificado.loc[df_modificado['Nombre'] == nuevo_nombre, 'Precio x Mayor'] = nuevo_precio_x_mayor
                            df_modificado.loc[df_modificado['Nombre'] == nuevo_nombre, 'Costo'] = nuevo_costo
                            df_modificado.loc[df_modificado['Nombre'] == nuevo_nombre, 'Stock'] = nuevo_stock
                            df_modificado.loc[df_modificado['Nombre'] == nuevo_nombre, 'Descripcion'] = nuevo_descripcion
                            df_modificado.loc[df_modificado['Nombre'] == nuevo_nombre, 'Categorias'] = nuevo_categorias.split(', ')
                            df_modificado.loc[df_modificado['Nombre'] == nuevo_nombre, 'Precio'] = nuevo_precio

                            st.success("✅ Producto modificado exitosamente.")

        # Botón para descargar el archivo Excel modificado
        st.header("💾 Descargar Archivo Modificado:")
        excel = convertir_a_excel(df_modificado)

        # Obtener la fecha y hora actual en horario
