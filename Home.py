if submit_egreso:
    if nombre_egreso.strip() == "":
        st.error("El nombre del egreso no puede estar vacío.")
    elif monto_egreso <= 0:
        st.error("El monto debe ser mayor a cero.")
    elif tipo_egreso == "Proveedor" and proveedor.strip() == "":
        st.error("El proveedor no puede estar vacío para un egreso a proveedor.")
    else:
        nuevo_egreso = {
            'Tipo': 'Egreso',
            'Nombre': nombre_egreso.strip(),
            'Detalle': detalle_egreso.strip(),
            'Monto': monto_egreso,
            'Fecha': fecha_egreso.strftime("%Y-%m-%d"),
            'Hora': hora_ingreso.strftime("%H:%M:%S")
        }
        st.session_state.df_administracion = st.session_state.df_administracion.append(nuevo_egreso, ignore_index=True)
        st.success(f"Egreso '{nombre_egreso}' registrado exitosamente.")
        st.session_state.df_administracion.to_excel('AdministracionSoop.xlsx', index=False)
        
        # Si el egreso es a un proveedor, actualizar el stock de productos
        if tipo_egreso == "Proveedor":
            # Asumiendo que el detalle_boleta tiene productos separados por comas en el formato "Codigo:Cantidad"
            try:
                items = detalle_boleta.split('\n')
                for item in items:
                    if ':' in item:
                        codigo, cantidad = item.split(':')
                        codigo = codigo.strip()
                        cantidad = int(cantidad.strip())
                        if codigo in st.session_state.df_productos['Codigo'].values:
                            st.session_state.df_productos.loc[st.session_state.df_productos['Codigo'] == codigo, 'Stock'] += cantidad
                        else:
                            st.warning(f"Producto con código '{codigo}' no encontrado.")
                # Guardar los cambios en el stock de productos
                st.session_state.df_productos.to_excel('archivo_modificado_productos_20240928_201237.xlsx', index=False)
                st.success("Stock de productos actualizado exitosamente.")
            except Exception as e:
                st.error(f"Error al actualizar el stock de productos: {e}")
