import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import unicodedata

# CONFIGURACIÓN GENERAL

st.set_page_config(page_title="Tablero de inventarios CLV", page_icon="📦", layout="wide")

ARCHIVO = "Datos_CLV_2026_Tec_v2.xlsx"
HOJA_EXISTENCIAS = "Existencias_04_09_2026"
HOJA_SALIDAS = "Salidas_Almacen"
HOJA_COMPRAS = "Histórico_Compras"

# Paleta del tablero
COLOR_PRINCIPAL = "#2A9D8F"   # verde azulado
COLOR_SECUNDARIO = "#264653"  # azul petróleo
COLOR_ACENTO = "#E76F51"      # coral
COLOR_SUAVE = "#E9C46A"       # mostaza
COLOR_FONDO = "#FAFAF7"
COLOR_TEXTO = "#3D3D3D"


# FUNCIONES DE APOYO

def limpiar_nombre(texto):
    # Pasa el nombre de una columna a minúsculas, sin acentos y con guion bajo
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = texto.replace(" ", "_").replace(".", "").replace("-", "_")
    return texto


def buscar_columna(df, opciones):
    # Regresa la primera columna del DataFrame que aparezca en la lista de opciones
    for opcion in opciones:
        if opcion in df.columns:
            return opcion
    return None


def estilo_grafica(ax, titulo, etiqueta_x="", etiqueta_y=""):
    # Aplica el mismo diseño a todas las gráficas
    ax.set_facecolor(COLOR_FONDO)
    ax.set_title(titulo, fontsize=13, fontweight="bold", color=COLOR_SECUNDARIO, loc="left", pad=12)
    ax.set_xlabel(etiqueta_x, fontsize=10, color=COLOR_TEXTO)
    ax.set_ylabel(etiqueta_y, fontsize=10, color=COLOR_TEXTO)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#BBBBBB")
    ax.spines["bottom"].set_color("#BBBBBB")
    ax.tick_params(colors=COLOR_TEXTO, labelsize=9)


def grafica_barras_horizontales(datos, titulo, etiqueta_x, color, formato="{:,.0f}"):
    # Barras horizontales ordenadas de mayor a menor con su valor al final
    alto = max(3.5, len(datos) * 0.38)
    fig, ax = plt.subplots(figsize=(8, alto))
    fig.patch.set_facecolor("white")
    datos = datos.sort_values(ascending=True)
    barras = ax.barh(datos.index.astype(str), datos.values, color=color, edgecolor="white", height=0.7)
    estilo_grafica(ax, titulo, etiqueta_x)
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)
    maximo = datos.max() if len(datos) > 0 else 0
    for barra in barras:
        valor = barra.get_width()
        ax.text(valor + maximo * 0.01, barra.get_y() + barra.get_height() / 2,
                formato.format(valor), va="center", fontsize=8, color=COLOR_TEXTO)
    if maximo > 0:
        ax.set_xlim(0, maximo * 1.15)
    fig.tight_layout()
    return fig


# CARGA DE DATOS
@st.cache_data
def cargar_datos():
    existencias = pd.read_excel(ARCHIVO, sheet_name=HOJA_EXISTENCIAS)
    salidas = pd.read_excel(ARCHIVO, sheet_name=HOJA_SALIDAS)
    compras = pd.read_excel(ARCHIVO, sheet_name=HOJA_COMPRAS)

    existencias.columns = [limpiar_nombre(c) for c in existencias.columns]
    salidas.columns = [limpiar_nombre(c) for c in salidas.columns]
    compras.columns = [limpiar_nombre(c) for c in compras.columns]
    return existencias, salidas, compras


existencias, salidas, compras = cargar_datos()

# Nombres de cada columna
OPC_MARCA = ["marca", "brand", "nombre_marca"]
OPC_PRODUCTO = ["nombre_articulo", "producto", "descripcion", "nombre_producto", "articulo", "descripcion_producto"]
OPC_EXISTENCIAS = ["existencias", "existencia", "cantidad", "stock", "unidades"]
OPC_VALOR = ["valor_total_inventario", "valor_total", "valor", "valor_inventario", "importe"]
OPC_CANT_SALIDA = ["cantidad", "unidades", "salidas", "cantidad_salida", "piezas"]
OPC_CANT_COMPRA = ["cantidad", "unidades", "cantidad_comprada", "piezas"]
OPC_PRECIO = ["precio_unitario", "precio", "costo_unitario", "precio_compra"]

# Existencias
ex_marca = buscar_columna(existencias, OPC_MARCA)
ex_producto = buscar_columna(existencias, OPC_PRODUCTO)
ex_unidades = buscar_columna(existencias, OPC_EXISTENCIAS)
ex_valor = buscar_columna(existencias, OPC_VALOR)

# Salidas
sa_marca = buscar_columna(salidas, OPC_MARCA)
sa_producto = buscar_columna(salidas, OPC_PRODUCTO)
sa_cantidad = buscar_columna(salidas, OPC_CANT_SALIDA)

# Compras
co_marca = buscar_columna(compras, OPC_MARCA)
co_producto = buscar_columna(compras, OPC_PRODUCTO)
co_cantidad = buscar_columna(compras, OPC_CANT_COMPRA)
co_precio = buscar_columna(compras, OPC_PRECIO)

# Limpieza básica
existencias[ex_marca] = existencias[ex_marca].fillna("Sin marca").astype(str).str.strip()
existencias[ex_producto] = existencias[ex_producto].fillna("Sin nombre").astype(str).str.strip()
existencias[ex_unidades] = pd.to_numeric(existencias[ex_unidades], errors="coerce").fillna(0)
existencias[ex_valor] = pd.to_numeric(existencias[ex_valor], errors="coerce").fillna(0)

salidas[sa_producto] = salidas[sa_producto].fillna("Sin nombre").astype(str).str.strip()
salidas[sa_cantidad] = pd.to_numeric(salidas[sa_cantidad], errors="coerce").fillna(0)
if sa_marca is not None:
    salidas[sa_marca] = salidas[sa_marca].fillna("Sin marca").astype(str).str.strip()

compras[co_cantidad] = pd.to_numeric(compras[co_cantidad], errors="coerce")
compras[co_precio] = pd.to_numeric(compras[co_precio], errors="coerce")
if co_marca is not None:
    compras[co_marca] = compras[co_marca].fillna("Sin marca").astype(str).str.strip()
if co_producto is not None:
    compras[co_producto] = compras[co_producto].fillna("Sin nombre").astype(str).str.strip()


# SIDEBAR: FILTROS
st.sidebar.header("Filtros")

lista_marcas = sorted(existencias[ex_marca].unique().tolist())
marcas_elegidas = st.sidebar.multiselect(
    "Marca",
    options=["Todas"] + lista_marcas,
    default=["Todas"],
    help="Elige una o varias marcas. 'Todas' muestra la base completa.",
)

texto_busqueda = st.sidebar.text_input(
    "Buscar producto",
    placeholder="Escribe parte del nombre",
    help="Filtra los productos que contengan este texto (no distingue mayúsculas).",
)

st.sidebar.divider()
st.sidebar.caption("Fuente de datos")
st.sidebar.markdown(f"**Archivo:** {ARCHIVO}")
st.sidebar.markdown(f"**Existencias:** {HOJA_EXISTENCIAS}")
st.sidebar.markdown(f"**Salidas:** {HOJA_SALIDAS}")
st.sidebar.markdown(f"**Compras:** {HOJA_COMPRAS}")
st.sidebar.divider()
st.sidebar.caption("Los filtros de marca y producto actualizan los KPIs y todas las gráficas.")

# Si no eligen nada o eligen "Todas", se usan todas las marcas
if len(marcas_elegidas) == 0 or "Todas" in marcas_elegidas:
    marcas_filtro = lista_marcas
else:
    marcas_filtro = marcas_elegidas


def aplicar_filtros(df, col_marca, col_producto):
    # Aplica los filtros del sidebar a cualquiera de las tres hojas
    resultado = df.copy()
    if col_marca is not None:
        resultado = resultado[resultado[col_marca].isin(marcas_filtro)]
    if col_producto is not None and texto_busqueda.strip() != "":
        resultado = resultado[resultado[col_producto].str.contains(texto_busqueda.strip(), case=False, na=False)]
    return resultado


ex_filtrado = aplicar_filtros(existencias, ex_marca, ex_producto)
sa_filtrado = aplicar_filtros(salidas, sa_marca, sa_producto)
co_filtrado = aplicar_filtros(compras, co_marca, co_producto)


# ENCABEZADO Y KPI's
st.title("📦 Tablero de inventarios CLV")
st.caption(f"Existencias, salidas y compras · Registros de existencias después de filtros: **{len(ex_filtrado):,}**")

productos_identificados = ex_filtrado[ex_producto].nunique()
unidades_totales = ex_filtrado[ex_unidades].sum()
valor_total = ex_filtrado[ex_valor].sum()
sin_existencias = (ex_filtrado[ex_unidades] <= 0).sum()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Productos identificados", f"{productos_identificados:,}", border=True)
k2.metric("Unidades en existencia", f"{unidades_totales:,.0f}", border=True)
k3.metric("Valor registrado", f"${valor_total:,.2f}", border=True)
k4.metric("Registros sin existencias", f"{sin_existencias:,}", border=True)

st.divider()

if len(ex_filtrado) == 0:
    st.warning("No hay registros con los filtros elegidos. Cambia la marca o el texto de búsqueda.")

tab1, tab2, tab3 = st.tabs(["📊 Resumen de existencias", "🚚 Salidas de almacén", "🛒 Compras y precios"])


# PESTAÑA 1 - RESUMEN DE EXISTENCIAS
with tab1:
    st.subheader("¿Cómo está repartido el inventario?")

    col_a, col_b = st.columns(2)

    with col_a:
        unidades_marca = ex_filtrado.groupby(ex_marca)[ex_unidades].sum()
        unidades_marca = unidades_marca[unidades_marca > 0].sort_values(ascending=False).head(15)
        if len(unidades_marca) > 0:
            fig1 = grafica_barras_horizontales(unidades_marca, "Unidades por marca (top 15)", "Unidades", COLOR_SECUNDARIO)
            st.pyplot(fig1)
            plt.close(fig1)
        else:
            st.info("Sin unidades para graficar.")

    with col_b:
        top_productos = ex_filtrado.groupby(ex_producto)[ex_unidades].sum()
        top_productos = top_productos[top_productos > 0].sort_values(ascending=False).head(10)
        # Se recortan nombres muy largos para que se lean bien
        nombres_cortos = []
        for nombre in top_productos.index:
            if len(nombre) > 32:
                nombres_cortos.append(nombre[:30] + "…")
            else:
                nombres_cortos.append(nombre)
        top_productos.index = nombres_cortos
        if len(top_productos) > 0:
            fig2 = grafica_barras_horizontales(top_productos, "Top 10 productos por unidades", "Unidades", COLOR_PRINCIPAL)
            st.pyplot(fig2)
            plt.close(fig2)
        else:
            st.info("Sin productos para graficar.")

    st.subheader("¿Qué marcas concentran el valor del inventario?")
    valor_marca = ex_filtrado.groupby(ex_marca)[ex_valor].sum()
    valor_marca = valor_marca[valor_marca > 0].sort_values(ascending=False).head(10)
    if len(valor_marca) > 0:
        # Gráfica tipo "lollipop" para diferenciarla de las barras anteriores
        valor_marca = valor_marca.sort_values(ascending=True)
        fig3, ax3 = plt.subplots(figsize=(10, max(3.5, len(valor_marca) * 0.45)))
        ax3.hlines(y=valor_marca.index, xmin=0, xmax=valor_marca.values, color=COLOR_SUAVE, linewidth=3)
        ax3.scatter(valor_marca.values, valor_marca.index, color=COLOR_ACENTO, s=110, zorder=3)
        estilo_grafica(ax3, "Valor registrado por marca (top 10)", "Valor registrado ($)")
        ax3.grid(axis="x", linestyle="--", alpha=0.4)
        maximo = valor_marca.max()
        for marca, valor in valor_marca.items():
            ax3.text(valor + maximo * 0.02, marca, f"${valor:,.0f}", va="center", fontsize=9, color=COLOR_TEXTO)
        ax3.set_xlim(0, maximo * 1.2)
        ax3.xaxis.set_major_formatter(mticker.StrMethodFormatter("${x:,.0f}"))
        fig3.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)

    st.info("Interpretación: las gráficas describen las existencias y el valor registrado en la fecha de corte. "
            "Por sí solas no demuestran sobreinventario ni baja rotación.")


# PESTAÑA 2 - SALIDAS DE ALMACÉN 
with tab2:
    st.subheader("¿Qué productos concentran las salidas?")

    salidas_producto = sa_filtrado.groupby(sa_producto)[sa_cantidad].sum()
    salidas_producto = salidas_producto[salidas_producto > 0].sort_values(ascending=False)

    if len(salidas_producto) == 0:
        st.warning("No hay salidas registradas con los filtros elegidos.")
    else:
        n_productos = st.slider(
            "Cantidad de productos visibles en el Pareto",
            min_value=5, max_value=60, value=20, step=5,
            help="Solo cambia cuántas barras se ven; el % acumulado se calcula con todos los productos.",
        )

        # Porcentaje acumulado con el universo completo de productos filtrados
        total_salidas = salidas_producto.sum()
        porcentaje_acum = salidas_producto.cumsum() / total_salidas * 100
        productos_80 = int((porcentaje_acum < 80).sum()) + 1
        if productos_80 > len(salidas_producto):
            productos_80 = len(salidas_producto)

        visibles = salidas_producto.head(n_productos)
        acum_visibles = porcentaje_acum.head(n_productos)

        nombres_pareto = []
        for nombre in visibles.index:
            if len(nombre) > 25:
                nombres_pareto.append(nombre[:23] + "…")
            else:
                nombres_pareto.append(nombre)

        fig4, ax4 = plt.subplots(figsize=(12, 5.5))
        posiciones = np.arange(len(visibles))
        # Las barras que forman el 80% se pintan de un color y el resto de otro
        colores = np.where(np.arange(len(visibles)) < productos_80, COLOR_PRINCIPAL, "#A8D5CF")
        ax4.bar(posiciones, visibles.values, color=colores, edgecolor="white")
        estilo_grafica(ax4, f"Pareto de salidas · primeros {len(visibles)} productos", "", "Unidades de salida")
        ax4.set_xticks(posiciones)
        ax4.set_xticklabels(nombres_pareto, rotation=60, ha="right", fontsize=8)
        ax4.grid(axis="y", linestyle="--", alpha=0.4)
        ax4.set_axisbelow(True)

        ax4b = ax4.twinx()
        ax4b.plot(posiciones, acum_visibles.values, color=COLOR_ACENTO, marker="o", markersize=5, linewidth=2)
        ax4b.axhline(80, color=COLOR_SUAVE, linestyle="--", linewidth=1.5)
        ax4b.text(len(visibles) - 0.5, 82, "80%", color="#B8860B", fontsize=9, ha="right")
        ax4b.set_ylim(0, 105)
        ax4b.set_ylabel("% acumulado del total", fontsize=10, color=COLOR_ACENTO)
        ax4b.tick_params(colors=COLOR_ACENTO, labelsize=9)
        ax4b.spines["top"].set_visible(False)
        fig4.tight_layout()
        st.pyplot(fig4)
        plt.close(fig4)

        m1, m2, m3 = st.columns(3)
        m1.metric("Unidades de salida", f"{total_salidas:,.0f}", border=True)
        m2.metric("Productos con salidas", f"{len(salidas_producto):,}", border=True)
        m3.metric("Productos para alcanzar 80%", f"{productos_80:,}", border=True)

        st.caption(f"Los primeros {len(visibles)} productos representan "
                   f"{acum_visibles.iloc[-1]:.2f}% del total de salidas. "
                   "La curva acumulada usa el universo completo de productos filtrados.")

        with st.expander("Consultar tabla de concentración"):
            tabla_pareto = pd.DataFrame({
                "Producto": salidas_producto.index,
                "Unidades de salida": salidas_producto.values,
                "% del total": (salidas_producto.values / total_salidas * 100).round(2),
                "% acumulado": porcentaje_acum.values.round(2),
            })
            st.dataframe(tabla_pareto, hide_index=True)

    st.divider()
    st.subheader("¿Cómo se reparten las salidas entre marcas?")

    if sa_marca is None:
        st.info("La hoja de salidas no tiene columna de marca.")
    else:
        salidas_marca = sa_filtrado.groupby(sa_marca)[sa_cantidad].sum()
        salidas_marca = salidas_marca[salidas_marca > 0].sort_values(ascending=False).head(15)
        if len(salidas_marca) > 0:
            fig5 = grafica_barras_horizontales(salidas_marca, "Salidas acumuladas por marca", "Unidades de salida", COLOR_ACENTO)
            st.pyplot(fig5)
            plt.close(fig5)

        with st.expander("Ver tabla filtrada de salidas"):
            st.dataframe(sa_filtrado, hide_index=True)

    st.info("Interpretación: el Pareto muestra qué productos concentran los movimientos de salida. "
            "No representa existencias actuales ni es una recomendación automática de compra.")


# PESTAÑA 3 - COMPRAS Y PRECIOS
with tab3:
    st.subheader("¿Qué cantidades se compran y cómo varían los precios?")

    co_validas = co_filtrado.dropna(subset=[co_cantidad, co_precio])
    co_validas = co_validas[(co_validas[co_cantidad] > 0) & (co_validas[co_precio] > 0)]

    if len(co_validas) == 0:
        st.warning("No hay registros de compra con los filtros elegidos.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Unidades compradas", f"{co_validas[co_cantidad].sum():,.0f}", border=True)
        c2.metric("Registros de compra", f"{len(co_validas):,}", border=True)
        c3.metric("Precio unitario mediano", f"${co_validas[co_precio].median():,.2f}", border=True)

        g1, g2 = st.columns(2)

        with g1:
            fig6, ax6 = plt.subplots(figsize=(7, 4.5))
            ax6.hist(co_validas[co_cantidad], bins=20, color=COLOR_SECUNDARIO, edgecolor="white", alpha=0.9)
            mediana_cant = co_validas[co_cantidad].median()
            ax6.axvline(mediana_cant, color=COLOR_ACENTO, linestyle="--", linewidth=2,
                        label=f"Mediana: {mediana_cant:,.0f}")
            estilo_grafica(ax6, "Unidades por registro de compra", "Unidades por operación", "Frecuencia")
            ax6.legend(frameon=False, fontsize=9)
            ax6.grid(axis="y", linestyle="--", alpha=0.4)
            ax6.set_axisbelow(True)
            fig6.tight_layout()
            st.pyplot(fig6)
            plt.close(fig6)

        with g2:
            fig7, ax7 = plt.subplots(figsize=(7, 4.5))
            ax7.scatter(co_validas[co_cantidad], co_validas[co_precio], color=COLOR_PRINCIPAL,
                        alpha=0.55, s=40, edgecolor="white", linewidth=0.5)
            estilo_grafica(ax7, "Cantidad vs. precio unitario", "Unidades compradas", "Precio unitario ($)")
            ax7.grid(linestyle="--", alpha=0.4)
            ax7.yaxis.set_major_formatter(mticker.StrMethodFormatter("${x:,.0f}"))
            fig7.tight_layout()
            st.pyplot(fig7)
            plt.close(fig7)

        st.caption("La dispersión puede mezclar productos distintos. Una relación visual no demuestra "
                   "que el volumen cause una reducción del precio.")

        with st.expander("Ver tabla filtrada de compras"):
            st.dataframe(co_validas, hide_index=True)

    st.info("Interpretación: el histograma muestra cómo se distribuyen las cantidades por operación y la "
            "dispersión cómo conviven cantidad y precio, pero no demuestra descuentos por volumen.")
