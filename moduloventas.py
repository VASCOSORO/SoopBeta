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

    # Buscador de productos
    st.subheader("Buscar y seleccionar producto")
    nombre_buscado = st.text_input("Buscar producto", value="", placeholder="Escribí el nombre del producto...")

    # Filtrar productos que coincidan con el texto buscado
    productos_filtrados = df_productos[df_productos['Producto'].str.contains(nombre_buscado, case=False, na=False)]

    # Agregar un valor vacío al principio del desplegable
    opciones = [""] + productos_filtrados['Producto'].tolist()

    # Seleccionar un producto desde el desplegable filtrado
    producto_seleccionado = st.selectbox("Selecciona el producto", opciones)

    # Filtrar el producto seleccionado
    if producto_seleccionado:
        producto = df_productos[df_productos['Producto'] == producto_seleccionado].iloc[0]

        # Mostrar y editar los atributos del producto
        st.subheader("Editar los detalles del producto")
        nombre = st.text_input("Nombre del Producto", producto['Producto'])

        # ID como número entero sin comas
        codigo = st.number_input("Código (ID)", value=int(producto['Codigo']), step=1, format="%d")

        # Precio sin decimales
        precio_mayor = st.number_input("Precio por Mayor", value=int(producto['Precio x Mayor']), step=1, format="%d")
        precio_costo = st.number_input("Precio de Costo", value=int(producto['Costo']), step=1, format="%d")

        # Costo FOB en dólares (usando coma como separador de miles y punto como separador de decimales)
        costo_dolares_fob = st.text_input("Costo en Dólares (FOB)", value=f"{producto.get('Costo FOB', 0):,.2f}".replace(",", "@").replace(".", ",").replace("@", "."))

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
            
            # Convertir de formato europeo (coma para decimales) a punto decimal y actualizar en el DataFrame
            df_productos.loc[df_productos['Producto'] == producto_seleccionado, 'Costo FOB'] = float(costo_dolares_fob.replace(".", "").replace(",", "."))

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
        st.write("Seleccioná un producto para editar sus detalles.")

else:
    st.write("El archivo no está disponible. Por favor, asegúrate de que el archivo '1083.xlsx' está en el directorio.")
