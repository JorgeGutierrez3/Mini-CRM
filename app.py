import streamlit as st
import sqlite3
import pandas as pd

# Función para capitalizar solo la primera letra de cada columna (mejora visual)
def capitalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [col.capitalize() for col in df.columns]
    return df.reset_index(drop=True)

# Conectar con la base de datos local y gestiona posibles errores de conexión
try:
    conn = sqlite3.connect("crm.db", check_same_thread=False)
    cursor = conn.cursor()
except sqlite3.Error as e:
    st.error(f"❌ Error al conectar con la base de datos: {e}")
    st.stop()

# Configurar la interfaz principal de Streamlit
st.set_page_config(page_title="CRM Básico", layout="centered")
st.title("CRM Básico - Clientes, Pedidos y Finanzas")
clientes_tab, pedidos_tab, finanzas_tab = st.tabs(["Clientes", "Pedidos", "Finanzas"])

# ====================
# 🧾 CLIENTES
# ====================
with clientes_tab:
    subopcion = st.radio("¿Qué quieres hacer?", [ "Buscar cliente", "Registrar cliente"], horizontal=True)

    
    # Buscar cliente en la base de datos con barra de búsqueda
    if subopcion == "Buscar cliente":
        st.subheader("Buscar cliente")
        # Filtrar clientes según búsqueda por nombre, apellido o email
        clientes_df = pd.read_sql_query("SELECT id, nombre, apellido, email, telefono, direccion FROM clientes", conn)
        busqueda = st.text_input("🔎 Buscar por nombre, apellido o email")

        # Si hay una búsqueda, filtrar el DataFrame de clientes, si no hay búsqueda, mostrar todos los clientes
        if busqueda:
            clientes_filtrados = clientes_df[
                clientes_df["nombre"].str.contains(busqueda, case=False, na=False) |
                clientes_df["apellido"].str.contains(busqueda, case=False, na=False) |
                clientes_df["email"].str.contains(busqueda, case=False, na=False)]
        else:
            clientes_filtrados = clientes_df

        # Mostrar los clientes filtrados sin la columna ID
        clientes_para_mostrar = clientes_filtrados.drop(columns=["id"])
        clientes_para_mostrar = capitalizar_columnas(clientes_para_mostrar)
        st.dataframe(clientes_para_mostrar, use_container_width=True, hide_index=True)

        # Mostrar pedidos del cliente seleccionado en la barra de búsqueda o en la lista de clientes con un selectbox
        if not clientes_filtrados.empty:

            # Mostrar encabezado con o sin nombre del cliente
            if busqueda:
                nombres = clientes_filtrados["nombre"] + " " + clientes_filtrados["apellido"]
                nombres_unicos = ", ".join(nombres.unique())
                st.markdown(f"### 📋 Pedidos registrados de: {nombres_unicos}")
            else:
                st.markdown("### 📋 Pedidos registrados")

            # Obtener IDs de los clientes filtrados
            ids_clientes = clientes_filtrados["id"].tolist()
            placeholders = ",".join(["?"] * len(ids_clientes))
            pedidos_query = f"""
                SELECT p.fecha, p.descripcion, p.monto, p.estado, c.nombre || ' ' || c.apellido AS cliente
                FROM pedidos p
                JOIN clientes c ON p.cliente_id = c.id
                WHERE c.id IN ({placeholders})
            """
            pedidos_cliente = pd.read_sql_query(pedidos_query, conn, params=ids_clientes)

            if not pedidos_cliente.empty:
                pedidos_cliente_para_mostrar = capitalizar_columnas(pedidos_cliente)
                pedidos_cliente_para_mostrar["Monto"] = pedidos_cliente_para_mostrar["Monto"].apply(lambda x: f"{x:.2f} €")
                st.dataframe(pedidos_cliente_para_mostrar, use_container_width=True, hide_index=True)

                if busqueda:
                    st.markdown(f"### 💰 Resumen financiero de: {nombres_unicos}")
                else:
                    st.markdown("### 💰 Resumen financiero")

                pedidos_cliente["monto"] = pd.to_numeric(pedidos_cliente["monto"], errors="coerce")
                total = pedidos_cliente["monto"].sum()
                pagado = pedidos_cliente[pedidos_cliente["estado"] == "Pagado"]["monto"].sum()
                pendiente = pedidos_cliente[pedidos_cliente["estado"] == "Pendiente"]["monto"].sum()
                cancelado = pedidos_cliente[pedidos_cliente["estado"] == "Cancelado"]["monto"].sum()

                st.metric("💰 Total de Pedidos", f"{total:.2f} €")
                st.metric("✅ Pagados", f"{pagado:.2f} €")
                st.metric("🕒 Pendientes", f"{pendiente:.2f} €")
                st.metric("❌ Cancelados", f"{cancelado:.2f} €")
            else:
                st.info("Los clientes encontrados no tienen pedidos registrados.")

    # Registrar cliente en la base de datos a partir de un formulario
    elif subopcion == "Registrar cliente":
        st.subheader("Registrar nuevo cliente")
        with st.form("cliente_form"):
            nombre = st.text_input("Nombre")
            apellido = st.text_input("Apellido")
            email = st.text_input("Email")
            telefono = st.text_input("Teléfono")
            direccion = st.text_input("Dirección")
            enviar = st.form_submit_button("Guardar")

            # Validar campos obligatorios y formato del email
            if enviar:
                if not nombre or not apellido or not email:
                    st.warning("⚠️ Nombre, apellido y email son campos obligatorios.")
                elif "@" not in email or "." not in email:
                    st.warning("⚠️ El email debe contener '@' y al menos un punto '.'")
                else:
                    try:
                        cursor.execute("""
                            INSERT INTO clientes (nombre, apellido, email, telefono, direccion) 
                            VALUES (?, ?, ?, ?, ?)
                        """, (nombre, apellido, email, telefono, direccion))
                        conn.commit()
                        st.success("✅ Cliente agregado correctamente")
                    except sqlite3.IntegrityError as e:
                        st.error(f"❌ El correo ya está registrado. {e}")
                    except Exception as e:
                        st.error(f"❌ Error inesperado: {e}")


# ====================
# 📦 PEDIDOS
# ====================

with pedidos_tab:
    st.subheader("Registrar nuevo pedido")

    # Registrar pedido en la base de datos a partir de un formulario vinculandolo con un cliente de la base de datos 
    clientes_df = pd.read_sql_query("SELECT id, nombre, apellido FROM clientes", conn)
    clientes_df["nombre_completo"] = clientes_df["nombre"] + " " + clientes_df["apellido"]
    opciones = clientes_df.set_index("id")["nombre_completo"].to_dict()

    with st.form("pedido_form"):
        descripcion = st.text_input("Descripción del pedido")
        monto = st.text_input("Monto del pedido")
        estado = st.selectbox("Estado del pedido", options=["Pagado", "Pendiente", "Cancelado"])
        cliente_id = st.selectbox("Cliente", options=list(opciones.keys()), format_func=lambda x: opciones[x])
        enviar = st.form_submit_button("Guardar")

        if enviar:
            try:
                monto_float = float(monto)
                if monto_float <= 0:
                    st.warning("⚠️ El monto debe ser mayor que cero.")

                if not descripcion or not monto:
                    st.warning("⚠️ Descripción y monto son campos obligatorios.")

                else:
                    cursor.execute("""
                        INSERT INTO pedidos (descripcion, monto, estado, cliente_id) 
                        VALUES (?, ?, ?, ?)
                    """, (descripcion, monto_float, estado, cliente_id))
                    conn.commit()
                    st.success("✅ Pedido agregado correctamente")
            except ValueError:
                st.error("❌ El monto debe ser un número válido.")
            except Exception as e:
                st.error(f"❌ Error inesperado al guardar el pedido: {e}")


# ====================
# 📊 FINANZAS
# ====================
with finanzas_tab:
    st.subheader("Resumen Financiero")
    # Mostrar métricas financieras de los TODOS pedidos registrados en la base de datos
    pedidos_df = pd.read_sql_query("SELECT monto, estado FROM pedidos", conn)

    if not pedidos_df.empty:
        pedidos_df["monto"] = pd.to_numeric(pedidos_df["monto"], errors="coerce")
        total = pedidos_df["monto"].sum()
        pagado = pedidos_df[pedidos_df["estado"] == "Pagado"]["monto"].sum()
        pendiente = pedidos_df[pedidos_df["estado"] == "Pendiente"]["monto"].sum()
        cancelado = pedidos_df[pedidos_df["estado"] == "Cancelado"]["monto"].sum()

        st.metric("💰 Total de Pedidos", f"{total:.2f} €")
        st.metric("✅ Pagados", f"{pagado:.2f} €")
        st.metric("🕒 Pendientes", f"{pendiente:.2f} €")
        st.metric("❌ Cancelados", f"{cancelado:.2f} €")
    else:
        st.info("No hay pedidos registrados.")
