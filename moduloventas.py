import streamlit as st
import pandas as pd

# Ruta del archivo en el directorio actual
archivo_excel = "1083.xlsx"

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

    # Seleccionar un producto para editar
    st.subheader("Seleccionar producto para editar")
    producto_seleccionado = st.selectbox("Selecciona el producto", df_productos['Producto'].unique())

    # Filtrar el producto seleccionado
    producto = df_productos[df_productos['Producto'] == producto_seleccionado].iloc[0]

    # Mostrar y editar los atributos del producto
    st.subheader("Editar los detalles del producto")
    nombre = st.text_input("Nombre del Producto", producto['Producto'])
    codigo = st.text_input("Código", producto['Codigo'])
    precio_mayor = st.number_input("Precio por Mayor", value=float(producto['Precio x Mayor']))
    precio_costo = st.number_input("Precio de Costo", value=float(producto['Costo']))
    costo_dolares = st.number_input("Costo en Dólares", value=float(producto.get('Costo en U$s', 0)))
    ubicacion = st.text_input("Ubicación", producto.get('Ubicación', ''))
    stock = st.number_input("Stock", value=int(producto['Stock']))
    categoria = st.text_input("Categoría", producto.get('Categoría', ''))
    descripcion = st.text_area("Descripción", producto.get('Descripción', ''))

    # Activar o desactivar el producto
    activo = st.checkbox("Producto Activo", value=producto.get('Activo', True))

    # Guardar los cambios en el DataFrame
    if st.button("Guardar cambios"):
        df_productos.loc[df_productos['Producto'] == producto_seleccionado, 'Producto'] = nombre
        df_productos.loc[df_productos['Producto'] == producto_seleccionado, 'Codigo'] = codigo
        df_productos.loc[df_productos['Producto'] == producto_seleccionado, 'Precio x Mayor'] = precio_mayor
        df_productos.loc[df_productos['Producto'] == producto_seleccionado, 'Costo'] = precio_costo
        df_productos.loc[df_productos['Producto'] == producto_seleccionado, 'Costo en U$s'] = costo_dolares
        df_productos.loc[df_productos['Producto'] == producto_seleccionado, 'Ubicación'] = ubicacion
        df_productos.loc[df_productos['Producto'] == producto_seleccionado, 'Stock'] = stock
        df_productos.loc[df_productos['Producto'] == producto_seleccionado, 'Categoría'] = categoria
        df_productos.loc[df_productos['Producto'] == producto_seleccionado, 'Descripción'] = descripcion
        df_productos.loc[df_productos['Producto'] == producto_seleccionado, 'Activo'] = activo
        st.success("Los cambios fueron guardados exitosamente.")

    # Opción para descargar el archivo modificado
    if st.button("Descargar base de datos actualizada"):
        df_productos.to_excel("productos_actualizados.xlsx", index=False)
        with open("productos_actualizados.xlsx", "rb") as file:
            st.download_button(
                label="Descargar archivo modificado",
                data=file,
                file_name="productos_actualizados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
else:
    st.write("El archivo no está disponible. Por favor, asegúrate de que el archivo '1083.xlsx' está en el directorio.")
