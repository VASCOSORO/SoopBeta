import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Home - Modulo Principal",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Título de la aplicación
st.title("🏠 Home - Módulo Principal")

# Instrucciones breves
st.subheader("Bienvenido, elige una herramienta para comenzar:")

# Sección con dos columnas para las herramientas
col1, col2 = st.columns(2)

with col1:
    st.header("Loader de CSV")
    st.write("Esta herramienta te permite cargar y modificar archivos CSV.")
    st.write("Haz clic en el botón para ir al Loader de CSV.")
    if st.button("Ir al Loader de CSV"):
        st.write("🔗 [Loader de CSV](https://soopbeta-jx7y7l6efyfjwfv4vbvk3a.streamlit.app/)")  # Enlace hacia el Loader de CSV

with col2:
    st.header("Modificador de Productos")
    st.write("Aquí puedes gestionar y modificar productos.")
    st.write("Haz clic en el botón para ir al Modificador de Productos.")
    if st.button("Ir al Modificador de Productos"):
        st.write("🔗 [Modificador de Productos](https://modulodepro.streamlit.app)")  # Enlace hacia el Modificador de Productos

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

# Llamamos a la función para el footer
agregar_footer()
