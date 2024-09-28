import streamlit as st
import pandas as pd

# Título de la aplicación
st.title("Sistema de Gestión de Pedidos")

# Cargar archivo de pedidos
uploaded_file = st.file_uploader("Subí el archivo de pedidos", type=["xlsx"])

if uploaded_file is not None:
    # Leer el archivo Excel
    df_pedidos = pd.read_excel(uploaded_file)

    # Mostrar la tabla original
    st.write("Tabla original de pedidos:")
    st.dataframe(df_pedidos)

    # Filtros para la gestión
    st.header("Filtros para modificar los pedidos")

    # Filtrar por vendedor
    vendedores = df_pedidos['Vendedor'].unique()
    vendedor_seleccionado = st.selectbox("Filtrar por vendedor", options=vendedores, index=0)
    df_filtrado = df_pedidos[df_pedidos['Vendedor'] == vendedor_seleccionado]

    # Filtrar por estado de pedido
    status_unicos = df_pedidos['Status'].unique()
    status_seleccionado = st.selectbox("Filtrar por status", options=status_unicos, index=0)
    df_filtrado = df_filtrado[df_filtrado['Status'] == status_seleccionado]

    # Mostrar la tabla filtrada
    st.write(f"Pedidos filtrados por vendedor: {vendedor_seleccionado} y status: {status_seleccionado}")
    st.dataframe(df_filtrado)

    # Modificar algunos campos
    st.header("Modificar pedidos seleccionados")

    # Seleccionar fila para editar
    fila_seleccionada = st.selectbox("Seleccionar un pedido por Id", options=df_filtrado['Id'].unique())
    pedido_seleccionado = df_pedidos[df_pedidos['Id'] == fila_seleccionada]

    # Modificar campos del pedido seleccionado
    nuevo_status = st.selectbox("Modificar el status", options=status_unicos, index=list(status_unicos).index(pedido_seleccionado['Status'].values[0]))
    nuevo_vendedor = st.selectbox("Modificar el vendedor", options=vendedores, index=list(vendedores).index(pedido_seleccionado['Vendedor'].values[0]))

    # Aplicar los cambios
    if st.button("Guardar cambios"):
        df_pedidos.loc[df_pedidos['Id'] == fila_seleccionada, 'Status'] = nuevo_status
        df_pedidos.loc[df_pedidos['Id'] == fila_seleccionada, 'Vendedor'] = nuevo_vendedor
        st.success(f"Pedido {fila_seleccionada} actualizado")

    # Opción para descargar el archivo modificado
    st.write("Descargá el archivo modificado en formato Excel:")
    df_pedidos.to_excel("pedidos_modificados.xlsx", index=False)
    with open("pedidos_modificados.xlsx", "rb") as file:
        st.download_button(
            label="Descargar archivo modificado",
            data=file,
            file_name="pedidos_modificados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
