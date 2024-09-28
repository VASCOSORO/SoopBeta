import streamlit as st
import pandas as pd
from datetime import datetime

# Ruta del archivo de productos y ventas
archivo_excel = "1083.xlsx"
archivo_ventas = "historial_ventas.xlsx"

# Cargar el archivo de productos
try:
    df_productos = pd.read_excel(archivo_excel)
    st.success(f"Archivo {archivo_excel} cargado con éxito.")
except FileNotFoundError:
    st.error(f"El archivo {archivo_excel} no se encontró en el directorio actual.")

# Si el archivo fue cargado exitosamente
if 'df_productos' in locals():
    st.header("Módulo de Ventas")
    
    # Paso 1: Selección de producto
    st.subheader("Paso 1: Seleccionar producto")
    nombre_buscado = st.text_input("Buscar producto", value="", placeholder="Escribí el nombre del producto...")

    # Filtrar productos que coincidan con el texto buscado
    productos_filtrados = df_productos[df_productos['Producto'].str.contains(nombre_buscado, case=False, na=False)]

    # Agregar un valor vacío al principio del desplegable
    opciones = [""] + productos_filtrados['Producto'].tolist()
    producto_seleccionado = st.selectbox("Seleccioná el producto", opciones)

    if producto_seleccionado:
        producto = df_productos[df_productos['Producto'] == producto_seleccionado].iloc[0]
        st.write(f"**Producto seleccionado:** {producto_seleccionado}")
        st.write(f"**Stock actual:** {producto['Stock']} unidades")

        # Paso 2: Registrar venta
        st.subheader("Paso 2: Registrar venta")
        cantidad_vendida = st.number_input("Cantidad vendida", min_value=1, max_value=int(producto['Stock']), step=1)
        precio_venta = st.number_input("Precio de venta por unidad", value=int(producto['Precio x Mayor']), step=1)

        # Paso 3: Confirmar la venta
        if st.button("Registrar venta"):
            nuevo_stock = producto['Stock'] - cantidad_vendida
            df_productos.loc[df_productos['Producto'] == producto_seleccionado, 'Stock'] = nuevo_stock

            # Crear registro de venta
            nueva_venta = {
                'Producto': producto_seleccionado,
                'Cantidad Vendida': cantidad_vendida,
                'Precio de Venta': precio_venta,
                'Fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # Guardar el historial de ventas
            try:
                df_ventas = pd.read_excel(archivo_ventas)
                df_ventas = df_ventas.append(nueva_venta, ignore_index=True)
            except FileNotFoundError:
                df_ventas = pd.DataFrame([nueva_venta])

            df_ventas.to_excel(archivo_ventas, index=False)
            st.success(f"Venta registrada: {cantidad_vendida} unidades de {producto_seleccionado} vendidas.")
            st.write(f"Nuevo stock de {producto_seleccionado}: {nuevo_stock} unidades")

        # Descargar base de datos actualizada
        if st.button("Descargar base de productos actualizada"):
            df_productos.to_excel("productos_actualizados.xlsx", index=False)
            with open("productos_actualizados.xlsx", "rb") as file:
                st.download_button(
                    label="Descargar archivo modificado",
                    data=file,
                    file_name="productos_actualizados.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        # Descargar historial de ventas
        if st.button("Descargar historial de ventas"):
            df_ventas.to_excel(archivo_ventas, index=False)
            with open("historial_ventas.xlsx", "rb") as file:
                st.download_button(
                    label="Descargar historial de ventas",
                    data=file,
                    file_name="historial_ventas.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
else:
    st.error("El archivo de productos no se cargó correctamente.")
