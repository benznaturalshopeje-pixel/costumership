import streamlit as st
import pytesseract
from PIL import Image

# Configuración de la página
st.set_page_config(page_title="Benz Natural - Generador WhatsApp", page_icon="💚", layout="wide")

st.title("💚 Benz Natural Shop - Automatización Logística")
st.markdown("Pegue los datos o suba el pantallazo para generar el mensaje exacto para Sognovitta.")

# --- 🛒 DICCIONARIO DE PRECIOS ACTUALIZADO ---
promociones = {
    "1 Unidad": {"total": "89.900", "saldo": "79.900"},
    "Lleva 3 Paga 2 (2+1 GRATIS)": {"total": "179.800", "saldo": "169.800"},
    "Lleva 5 Paga 3 (3+2 GRATIS)": {"total": "269.700", "saldo": "259.700"}
}

# --- BARRA LATERAL: CONTROLES DE LA APP ---
st.sidebar.header("⚙️ Configuración del Mensaje")

etapa = st.sidebar.selectbox(
    "Etapa del Proceso:",
    ["Confirmación de Compra", "Envío de Guía", "Novedad de Transportadora", "Clientes Borradores"]
)

# Control de Promociones
promo_seleccionada = st.sidebar.selectbox(
    "Seleccione la Oferta Vendida:",
    list(promociones.keys())
)

# Sacamos los precios dinámicamente
precio_total = promociones[promo_seleccionada]["total"]
precio_saldo = promociones[promo_seleccionada]["saldo"]

# Control B: Perfil de riesgo
perfil_cliente = None
if etapa == "Confirmación de Compra":
    perfil_cliente = st.sidebar.radio(
        "Perfil del Cliente (Pago Contraentrega):",
        ["Normal (Historial Limpio)", "Riesgo (Devoluciones Previas)"]
    )

st.sidebar.divider()
st.sidebar.info("💡 **Consejo:** Use el botón de 'Copy' en la esquina de la caja de texto final para WhatsApp.")

# --- FUNCIÓN PA' SACAR LOS DATOS (CON REGLA EXTRA PARA LA GUÍA) ---
def parsear_datos(texto):
    datos = {"nombre": "[NOMBRE]", "direccion": "[DIRECCIÓN]", "ciudad": "[CIUDAD]", "guia": "[NÚMERO DE GUÍA]"}
    if not texto.strip():
        return datos

    lineas = texto.split('\n')
    lineas_limpias = [linea.strip() for linea in lineas if linea.strip()]
    
    temp_nombre = ""
    temp_apellido = ""

    for i, linea in enumerate(lineas_limpias):
        linea_lower = linea.lower()
        
        # 1. Pescar Nombre
        if "nombre" in linea_lower:
            if i + 1 < len(lineas_limpias):
                temp_nombre = lineas_limpias[i+1]
        
        # 2. Pescar Apellido
        elif "apellido" in linea_lower:
            if i + 1 < len(lineas_limpias):
                temp_apellido = lineas_limpias[i+1]

        # 3. Pescar Dirección Exacta y arreglar el OCR
        elif "direc" in linea_lower or "exacta" in linea_lower:
            if i + 1 < len(lineas_limpias):
                dir_cruda = lineas_limpias[i+1].upper()
                dir_limpia = dir_cruda.replace("1T", "#").replace("IT", "#")
                datos["direccion"] = dir_limpia

        # 4. Pescar Ciudad / City
        elif "city" in linea_lower or "ciudad" in linea_lower or "municipio" in linea_lower:
            if i + 1 < len(lineas_limpias):
                datos["ciudad"] = lineas_limpias[i+1].upper()

        # 5. Pescar Número de Guía (Por si viene en el texto/OCR)
        elif "guia" in linea_lower or "guía" in linea_lower or "tracking" in linea_lower or "remision" in linea_lower:
            if i + 1 < len(lineas_limpias):
                datos["guia"] = lineas_limpias[i+1].upper()
            
    # Armar nombre completo
    if temp_nombre or temp_apellido:
        datos["nombre"] = f"{temp_nombre} {temp_apellido}".strip().title()
        
    return datos

# --- TABS: ENTRADA DE DATOS ---
tab1, tab2 = st.tabs(["📝 Pegar Texto", "📸 Subir Imagen (OCR)"])

texto_crudo = ""

with tab1:
    texto_crudo_input = st.text_area("Pegue el texto crudo aquí (de Shopify/Dropi):", height=200, placeholder="Copie todo el detalle del pedido...")
    if texto_crudo_input:
        texto_crudo = texto_crudo_input

with tab2:
    imagen_subida = st.file_uploader("Suba el pantallazo del pedido o de la guía (formatos PNG, JPG):", type=["png", "jpg", "jpeg"])
    if imagen_subida is not None:
        try:
            image = Image.open(imagen_subida)
            st.image(image, caption="Imagen cargada", use_container_width=True)
            with st.spinner("Leyendo el texto del pantallazo, espere un momentico..."):
                texto_crudo = pytesseract.image_to_string(image, lang='spa') 
                st.success("¡Texto extraído melo!")
                with st.expander("Ver texto crudo extraído (OCR)"):
                    st.text(texto_crudo)
        except Exception as e:
            st.error(f"Pailas mano, hubo un error procesando la imagen. Error: {e}")

# Procesamos datos sacados
datos_extraidos = parsear_datos(texto_crudo)

st.divider()

# --- VERIFICACIÓN DE DATOS DINÁMICOS ANTES DE GENERAR ---
st.subheader("✍️ 1. Verifique los datos extraídos")
st.info("Ajuste los datos si el OCR no leyó bien alguna parte.")

# Inicialización de variables para que no se tote el script
nombre_final = datos_extraidos["nombre"]
direccion_final = datos_extraidos["direccion"]
ciudad_final = datos_extraidos["ciudad"]
guia_final = datos_extraidos["guia"]

# Aquí está el truco mano: cambian los campos según la etapa elegida
if etapa == "Clientes Borradores":
    nombre_final = st.text_input("Nombre del Cliente Borrador:", value=datos_extraidos["nombre"])

elif etapa == "Envío de Guía":
    col1, col2, col3 = st.columns(3)
    with col1:
        nombre_final = st.text_input("Nombre del Cliente:", value=datos_extraidos["nombre"])
    with col2:
        ciudad_final = st.text_input("Ciudad/Municipio:", value=datos_extraidos["ciudad"])
    with col3:
        guia_final = st.text_input("Número de Guía:", value=datos_extraidos["guia"])

else:  # Confirmación de Compra o Novedad de Transportadora
    col1, col2, col3 = st.columns(3)
    with col1:
        nombre_final = st.text_input("Nombre del Cliente:", value=datos_extraidos["nombre"])
    with col2:
        direccion_final = st.text_input("Dirección de Envío:", value=datos_extraidos["direccion"])
    with col3:
        ciudad_final = st.text_input("Ciudad/Municipio:", value=datos_extraidos["ciudad"])

# --- LÓGICA DE PLANTILLAS (OUTPUT FINAL) ---
st.subheader("💬 2. Mensaje de WhatsApp Generado")

mensaje_final = ""

if etapa == "Confirmación de Compra":
    if perfil_cliente == "Normal (Historial Limpio)":
        mensaje_final = f"¡Buen día {nombre_final}, soy Angie de Benz Natural Shop, gracias por confiar! 💚 Necesitamos que nos confirmes si estos datos son correctos para enviarte tu pedido de Sognovitta ({promo_seleccionada}):\n📍 Datos de envío: Dirección: {direccion_final}, Ciudad: {ciudad_final}.\nEl valor a pagar al recibir es de ${precio_total} COP. Recuerda que el pago es únicamente en EFECTIVO. Por favor, responda con 'CONFIRMAR' si los datos están correctos para despachar hoy mismo."
    else: # Riesgo
        mensaje_final = f"¡Buen día {nombre_final}, soy Angie de Benz Natural Shop, gracias por confiar! 💚 Necesitamos que nos confirmes si estos datos son correctos para enviarte tu pedido de Sognovitta ({promo_seleccionada}):\n📍 Datos de envío: Dirección: {direccion_final}, Ciudad: {ciudad_final}.\n⚠️ Nota de despacho: Debido a la altísima demanda y para asegurar tu unidad, requerimos un pequeño anticipo de seguridad de $10.000 COP para generar la guía hoy mismo. Este valor se descuenta de tu total, por lo que al recibir el producto solo pagarás el saldo de ${precio_saldo} COP en efectivo al mensajero. Por favor, responda con 'CONFIRMAR' para apartar tu pedido."

elif etapa == "Envío de Guía":
    mensaje_final = f"¡Hola {nombre_final}! 🚛 Excelente noticia, tu pedido de Sognovitta ({promo_seleccionada}) ya va en camino hacia {ciudad_final}. Tu número de guía es: {guia_final}. Recuerda tener listo el efectivo (${precio_total} COP) para cuando llegue el mensajero. ¡Cualquier duda nos escribes!"

elif etapa == "Novedad de Transportadora":
    mensaje_final = f"¡Hola {nombre_final}! 🚨 La transportadora nos informa que tu pedido ya está en {ciudad_final} listo para entrega, pero no han podido contactarte. Por favor, confírmanos tu disponibilidad en {direccion_final} para coordinar la entrega y que no devuelvan el paquete."

elif etapa == "Clientes Borradores":
    mensaje_final = f"¡Hola {nombre_final}! 💚 Te saludamos de Benz Natural Shop. Notamos que estuviste revisando nuestro tratamiento Sognovitta, pero no alcanzaste a finalizar tu pedido. ¡Queremos ayudarte! Cuéntanos si tuviste algún problema con la página o si te quedó alguna duda sobre los beneficios del producto para ayudarte a completarlo hoy mismo con envío gratis."

st.code(mensaje_final, language="text")
