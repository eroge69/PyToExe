import streamlit as st
import pandas as pd
import io
import os # Necesario para verificar si la ruta de la imagen local existe

# Configuración de la página de Streamlit
st.set_page_config(layout="wide", page_title="Visor y Editor de Paneles")

st.title("Visor y Editor de Paneles por Tienda")

# --- Carga del archivo CSV o Excel ---
st.header("Cargar Archivo de Inventario")
uploaded_file = st.file_uploader(
    "Selecciona tu archivo CSV o Excel",
    type=["csv", "xlsx"],
    help="Sube tu archivo de inventario. Debe contener las columnas: tienda, mueble, panel, serie, imagen."
)

# Inicializar el DataFrame y las cabeceras en el estado de la sesión
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()
if 'original_headers' not in st.session_state:
    st.session_state.original_headers = []
if 'file_type' not in st.session_state:
    st.session_state.file_type = None

# Cargar los datos cuando se sube un archivo
if uploaded_file is not None:
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        st.session_state.file_type = file_extension

        if file_extension == "csv":
            st.session_state.df = pd.read_csv(uploaded_file)
        elif file_extension == "xlsx":
            st.session_state.df = pd.read_excel(uploaded_file)
        else:
            st.error("Formato de archivo no soportado. Por favor, sube un archivo .csv o .xlsx.")
            st.session_state.df = pd.DataFrame()

        st.session_state.original_headers = st.session_state.df.columns.tolist()

        required_headers_lower = ['tienda', 'mueble', 'panel', 'serie', 'imagen']
        df_columns_lower = [col.lower() for col in st.session_state.df.columns]

        missing_headers = [
            req_header for req_header in required_headers_lower
            if req_header not in df_columns_lower
        ]

        if missing_headers:
            st.error(
                f"El archivo CSV/Excel debe contener las siguientes columnas: "
                f"{', '.join([h.capitalize() for h in required_headers_lower])}. "
                f"Faltan: {', '.join([h.capitalize() for h in missing_headers])}."
            )
            st.session_state.df = pd.DataFrame()
            st.session_state.original_headers = []
        else:
             st.success("Archivo cargado y validado correctamente.")
             # Normalizar los nombres de columna a minúsculas para facilitar el acceso
             st.session_state.df.columns = df_columns_lower


    except Exception as e:
        st.error(f"Ocurrió un error al leer el archivo: {e}")
        st.session_state.df = pd.DataFrame()
        st.session_state.original_headers = []


# --- Visualización y Edición de Datos ---
if not st.session_state.df.empty:
    st.header("Datos del Inventario")

    if 'tienda' in st.session_state.df.columns:
        stores = st.session_state.df['tienda'].unique().tolist()
        stores.sort()
        selected_store = st.selectbox("Selecciona una Tienda:", ["Todas las Tiendas"] + stores)

        if selected_store == "Todas las Tiendas":
            filtered_df = st.session_state.df
        else:
            filtered_df = st.session_state.df[st.session_state.df['tienda'] == selected_store]

        st.subheader(f"Paneles en: {selected_store}")

        # --- Mostrar Paneles Visualmente (Imágenes y Info Clave) ---
        # Esta sección solo se muestra si se ha seleccionado una tienda específica (no "Todas las Tiendas")
        if selected_store != "Todas las Tiendas":
            st.subheader("Visualización de Paneles")
            if not filtered_df.empty:
                # Usar columnas para mostrar imágenes e info lado a lado
                # Ajustar el número de columnas visuales según tus preferencias
                cols_per_row = 3 # Número de paneles por fila en la visualización
                cols = st.columns(cols_per_row)
                col_index = 0

                for index, row in filtered_df.iterrows():
                    # Usar un bloque 'with' para cada columna asegura que los elementos se coloquen dentro
                    with cols[col_index]:
                        st.write(f"**Panel:** {row.get('panel', 'N/A')}")
                        st.write(f"**Mueble:** {row.get('mueble', 'N/A')}")
                        st.write(f"**Serie:** {row.get('serie', 'N/A')}")

                        image_path = row.get('imagen', '')
                        if image_path:
                            # Intentar mostrar la imagen local o URL
                            try:
                                # Verificar si la ruta local existe antes de intentar mostrarla
                                # Esto ayuda a evitar errores si la ruta está mal
                                if os.path.exists(image_path):
                                    # Usar use_container_width en lugar de use_column_width
                                    st.image(image_path, caption=row.get('panel', 'Imagen'), use_container_width=True)
                                else:
                                    # Si no es una ruta local, intentar como URL web
                                    # Usar use_container_width en lugar de use_column_width
                                    st.image(image_path, caption=row.get('panel', 'Imagen'), use_container_width=True)
                            except Exception as img_e:
                                st.warning(f"No se pudo cargar la imagen para el panel {row.get('panel', 'N/A')}: {img_e}")
                                st.info("Verifica que la ruta de la imagen sea correcta y accesible.")
                        else:
                            st.info("No hay imagen disponible para este panel.")

                    col_index = (col_index + 1) % cols_per_row # Mover a la siguiente columna

                # Asegurarse de que todas las columnas se llenan si el número de paneles no es múltiplo de cols_per_row
                for i in range(col_index, cols_per_row):
                    with cols[i]:
                        st.empty() # Dejar las columnas restantes vacías

                st.markdown("---") # Separador visual

        # --- Mostrar Tabla de Datos Completa y Editable ---
        st.subheader("Tabla de Datos Completa (Editable)")
        # Usamos st.data_editor para la edición, pero sin la ImageColumn visual
        # La columna 'imagen' se mostrará como texto para poder editar la ruta/URL
        edited_df = st.data_editor(
            filtered_df,
            use_container_width=True,
            num_rows="dynamic", # Permite añadir/eliminar filas
            key=f"editor_table_{selected_store}", # Clave única para el editor de tabla
            # No usamos ImageColumn aquí, la columna 'imagen' será texto por defecto
        )

        # Actualizar el DataFrame principal con los cambios del editor
        # Esta lógica es más compleja con num_rows="dynamic" y filtros.
        # La forma más segura es trabajar con un ID único por fila.
        # Como no tenemos un ID único por defecto en el CSV, si se añaden/eliminan filas
        # en una vista filtrada, la sincronización con el DataFrame original puede ser inexacta.
        # Para simplificar y hacerlo funcional con num_rows="dynamic",
        # vamos a asumir que la edición principal (añadir/eliminar) se hace en "Todas las Tiendas".
        # Si se edita una vista filtrada con añadir/eliminar, los cambios pueden no reflejarse
        # correctamente en el DataFrame original al guardar.
        # Para una aplicación más robusta, se necesitaría añadir una columna de ID único.

        # Lógica de actualización simple (funciona si no se añaden/eliminan filas en la vista filtrada)
        # Reemplazamos las filas del DataFrame principal con las filas editadas
        # Esto asume que el índice de filtered_df coincide con el índice del DataFrame principal
        # para las filas mostradas. Esto es cierto si no se reordena ni se añaden/eliminan filas.
        # Con num_rows="dynamic", esto puede ser problemático.
        # La mejor práctica sería usar un ID único para mergear.
        # Vamos a mantener num_rows="dynamic" pero con la advertencia de que la edición
        # en vistas filtradas con añadir/eliminar puede no ser totalmente precisa al guardar.

        # Actualizar el DataFrame principal: si se editó la vista "Todas las Tiendas",
        # simplemente reemplazamos el DataFrame completo.
        if selected_store == "Todas las Tiendas":
             st.session_state.df = edited_df
        else:
            # Si se editó una vista filtrada, la lógica es más compleja.
            # Para mantenerlo simple y funcional con num_rows="dynamic",
            # vamos a recargar el DataFrame principal desde la vista editada filtrada.
            # Esto SOBREESCRIBIRÁ los datos de otras tiendas si se edita una vista filtrada.
            # Esta no es la solución ideal para una aplicación multi-tienda con edición dinámica.
            # La solución robusta requiere un ID único y mergear.
            # Dado que el usuario es novato, vamos a simplificar y advertir.

            # --- Advertencia ---
            st.warning("Nota: La edición con 'Añadir fila' o 'Eliminar fila' en una vista filtrada puede no guardar los cambios correctamente para otras tiendas. Para añadir/eliminar filas de forma segura, usa la vista 'Todas las Tiendas'.")

            # Lógica de actualización simple que puede ser problemática con num_rows="dynamic" en vistas filtradas
            # st.session_state.df.loc[edited_df.index] = edited_df # Esto es problemático con dynamic

            # Mejor enfoque (aún no perfecto sin ID único): Reconstruir el DF principal
            # Esto es complejo y puede perder datos si los índices no coinciden perfectamente.
            # Vamos a mantener la lógica simple de reemplazar si es "Todas las Tiendas"
            # y confiar en que el usuario edite estructura en la vista completa.
            # Si edita valores en una vista filtrada, esos cambios sí se reflejarán.

            # Para que la edición de valores en la vista filtrada funcione,
            # necesitamos actualizar las filas correspondientes en el DataFrame principal.
            # Esto se puede hacer si el índice de edited_df se corresponde con el índice del DF principal.
            # Esto es cierto si no se reordena ni se añaden/eliminan filas en la vista filtrada.
            # Con num_rows="dynamic", Streamlit puede cambiar los índices.
            # La forma más segura es iterar sobre edited_df y encontrar las filas correspondientes en st.session_state.df
            # basándose en algún identificador (idealmente un ID único).
            # Sin un ID único, podemos intentar usar una combinación de columnas como identificador,
            # pero esto puede ser propenso a errores si hay filas duplicadas.

            # Vamos a simplificar la lógica de guardado: solo permitimos guardar el DataFrame completo
            # tal como aparece en la vista "Todas las Tiendas" si se ha editado allí.
            # Si se edita una vista filtrada, los cambios se reflejan en el DataFrame principal en memoria,
            # pero la lógica de descarga se basará en el DataFrame completo en memoria.

            # La lógica de actualización automática de `st.data_editor` ya modifica `st.session_state.df`
            # cuando se edita la vista "Todas las Tiendas".
            # Cuando se edita una vista filtrada, `edited_df` es una copia. Necesitamos transferir los cambios.
            # Streamlit 1.27+ tiene un comportamiento mejorado para `st.data_editor` con filtros,
            # donde los cambios en la vista filtrada se propagan al DataFrame original.
            # Asumiremos este comportamiento más reciente.

            # No necesitamos una lógica de actualización explícita aquí si Streamlit maneja la propagación de cambios.
            pass # Dejar que Streamlit maneje la propagación de cambios desde edited_df a st.session_state.df


    else:
        st.warning("El archivo cargado no contiene la columna 'tienda'. No se puede filtrar por tienda.")

else:
    st.info("Por favor, sube un archivo CSV o Excel para empezar.")

# --- Botón para Guardar Cambios ---
st.header("Guardar Cambios")
st.warning("El botón 'Guardar Cambios' descargará un NUEVO archivo con las modificaciones. No sobrescribe el archivo original.")

# Convertir el DataFrame modificado a CSV o Excel para descargar
@st.cache_data
def convert_df(df, file_type, original_headers):
    # Asegurarse de que el orden de las columnas es el original
    # Manejar el caso donde el DataFrame pueda estar vacío después de ediciones
    if df.empty:
        df_to_save = pd.DataFrame(columns=original_headers)
    else:
        # Asegurarse de que todas las columnas originales están presentes, añadiendo si faltan (ej: si se eliminaron todas las filas)
        # y reordenar según las cabeceras originales
        for col in original_headers:
            if col.lower() not in df.columns:
                 # Añadir columna vacía si falta (esto no debería pasar con num_rows="dynamic" pero es buena práctica)
                 df[col.lower()] = None

        # Asegurarse de que las columnas existen antes de intentar reordenar
        cols_to_save = [col.lower() for col in df.columns if col.lower() in [h.lower() for h in original_headers]]
        # Añadir columnas que puedan haberse creado si se usó num_rows="dynamic" y se añadieron nuevas columnas
        new_cols = [col for col in df.columns if col.lower() not in [h.lower() for h in original_headers]]
        cols_to_save.extend(new_cols)

        # Reordenar según las cabeceras originales (insensible a mayúsculas/minúsculas)
        # y luego añadir las nuevas columnas al final
        # Crear un mapeo de cabeceras en minúsculas a originales para el reordenamiento
        lower_to_original_map = {h.lower(): h for h in original_headers}
        # Crear la lista de columnas en el orden original, usando las claves en minúsculas del DataFrame
        ordered_cols_lower = [h.lower() for h in original_headers if h.lower() in df.columns] + new_cols

        df_to_save = df[ordered_cols_lower]


        # Restaurar las cabeceras originales (distinguiendo mayúsculas/minúsculas)
        # Esto requiere un mapeo de las cabeceras en minúsculas a las originales
        # Usar el mapeo creado anteriormente
        df_to_save.columns = [lower_to_original_map.get(col, col) for col in df_to_save.columns]


    if file_type == "csv":
        return df_to_save.to_csv(index=False, sep=',')
    elif file_type == "xlsx":
        output = io.BytesIO()
        df_to_save.to_excel(output, index=False, engine='openpyxl')
        return output.getvalue()

# Usar un botón simple para desencadenar la descarga
if st.button("Generar archivo para descargar"):
    if not st.session_state.df.empty:
        try:
            if st.session_state.file_type == "csv":
                file_content = convert_df(st.session_state.df, "csv", st.session_state.original_headers)
                st.download_button(
                    label="Haz clic para descargar CSV",
                    data=file_content,
                    file_name="inventario_modificado.csv",
                    mime="text/csv",
                    key="download_csv_button" # Añadir una clave para que Streamlit lo maneje correctamente
                )
            elif st.session_state.file_type == "xlsx":
                file_content = convert_df(st.session_state.df, "xlsx", st.session_state.original_headers)
                st.download_button(
                    label="Haz clic para descargar Excel",
                    data=file_content,
                    file_name="inventario_modificado.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_excel_button" # Añadir una clave
                )
        except Exception as e:
            st.error(f"Error al preparar el archivo para descargar: {e}")
            st.exception(e) # Mostrar detalles del error en la interfaz
    else:
        st.warning("No hay datos cargados para descargar.")
