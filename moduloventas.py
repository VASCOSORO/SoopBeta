import streamlit as st
import pandas as pd
from datetime import datetime

# Ruta del archivo de productos
archivo_excel = "1083.xlsx"
archivo_ventas = "historial_ventas.xlsx"

# Verificar si el archivo existe en el directorio
try:
    df_productos = pd.read_excel(archivo_excel)
    st.success(f"Archivo {archivo_excel} cargado con éxito.")
except FileNotFoundError:
    st.error(f"El archivo {archivo_excel} no se encontró en el directorio actual.")

# Mostrar la tabla original de productos si el archivo fue cargado exitosamente
if 'df_productos' in locals():
    st.write("Datos actuales de la base de productos:")
    st.dataframe(df_productos)

    # Buscador de productos
    st.subheader("Buscar y seleccionar producto para registrar venta")
    nombre_buscado = st.text_input("Buscar producto", value="", placeholder="Escribí el nombre del producto...")

    # Filtrar productos que coincidan con el texto buscado
    productos_filtrados = df_productos[df_productos['Producto'].str.contains(nombre_buscado, case=False, na=False)]

    # Agregar un valor vacío al principio del desplegable
    opciones = [""] + productos_filtrados['Producto'].tolist()

    # Seleccionar un producto desde el desplegable filtrado
    producto_seleccionado = st.selectbox("Selecciona el producto", opciones)

    # Registro de venta
    if producto_seleccionado:
        producto = df_productos[df_productos['Producto'] == producto_seleccionado].iloc[0]
        st.subheader("Registrar venta")

        # Mostrar el stock actual
        st.write(f"Stock actual: {producto['Stock']}")

        # Ingresar cantidad vendida
        cantidad_vendida = st.number_input("Cantidad vendida", min_value=1, max_value=int(producto['Stock']), step=1)

        # Ingresar precio de venta
        precio_venta = st.number_input("Precio de Venta", value=int(producto['Precio x Mayor']), step=1, format="%d")

        # Registrar la venta
        if st.button("Registrar venta"):
            # Actualizar stock
            nuevo_stock = producto['Stock'] - cantidad_vendida
            df_productos.loc[df_productos['Producto'] == producto_seleccionado, 'Stock'] = nuevo_stock
            st.success(f"Venta registrada. Nuevo stock de {producto_seleccionado}: {nuevo_stock}")

            # Guardar el historial de ventas
            nueva_venta = {
                'Producto': producto_seleccionado,
                'Cantidad Vendida': cantidad_vendida,
                'Precio de Venta': precio_venta,
                'Fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # Verificar si existe el archivo de historial de ventas y actualizarlo
            try:
                df_ventas = pd.read_excel(archivo_ventas)
                df_ventas = df_ventas.append(nueva_venta, ignore_index=True)
            except FileNotFoundError:
                df_ventas = pd.DataFrame([nueva_venta])

            df_ventas.to_excel(archivo_ventas, index=False)
            st.success("Venta registrada en el historial.")

        # Opción para descargar la base de datos actualizada
        if st.button("Descargar base de datos actualizada"):
            df_productos.to_excel("productos_actualizados.xlsx", index=False)
            with open("productos_actualizados.xlsx", "rb") as file:
                st.download_button(
                    label="Descargar archivo modificado",
                    data=file,
                    file_name="productos_actualizados.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        # Opción para descargar el historial de ventas
        if st.button("Descargar historial de ventas"):
            df_ventas.to_excel("historial_ventas.xlsx", index=False)
            with open("historial_ventas.xlsx", "rb") as file:
                st.download_button(
                    label="Descargar historial de ventas",
                    data=file,
                    file_name="historial_ventas.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

else:
    st.write("El archivo no está disponible. Por favor, asegúrate de que el archivo '1083.xlsx' está en el directorio.")
