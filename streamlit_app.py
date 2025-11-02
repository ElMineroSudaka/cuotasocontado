import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Calculadora: Contado vs Cuotas",
    page_icon="💰",
    layout="wide"
)

# Título principal
st.title("💰 Calculadora: ¿Contado o Cuotas?")
st.markdown("Analiza si te conviene comprar de contado o financiar en cuotas considerando la inflación")

# Sidebar para inputs
st.sidebar.header("📊 Ingresa los datos")

# Inputs principales
precio_contado = st.sidebar.number_input(
    "Precio de contado ($)", 
    value=4500000, 
    min_value=1000, 
    step=100000,
    format="%d"
)

precio_cuotas = st.sidebar.number_input(
    "Precio total en cuotas ($)", 
    value=5760000, 
    min_value=1000, 
    step=100000,
    format="%d"
)

cantidad_cuotas = st.sidebar.number_input(
    "Cantidad de cuotas", 
    value=24, 
    min_value=1, 
    max_value=60,
    step=1
)

inflacion_mensual = st.sidebar.number_input(
    "Inflación mensual estimada (%)", 
    value=1.9, 
    min_value=0.0, 
    max_value=20.0,
    step=0.1,
    format="%.1f"
) / 100

# Inputs adicionales en expander
with st.sidebar.expander("⚙️ Configuración avanzada"):
    tasa_inversion = st.number_input(
        "Tasa de inversión alternativa mensual (%)",
        value=2.0,
        min_value=0.0,
        max_value=20.0,
        step=0.1,
        help="Si tienes el dinero, ¿cuánto podrías ganar invirtiéndolo?",
        format="%.1f"
    ) / 100
    
    considerar_inversion = st.checkbox(
        "Considerar inversión alternativa",
        value=False,
        help="Analizar el costo de oportunidad de usar el dinero"
    )

# Cálculos principales
sobreprecio = precio_cuotas - precio_contado
porcentaje_sobreprecio = (sobreprecio / precio_contado) * 100
valor_cuota = precio_cuotas / cantidad_cuotas
tasa_financiacion_total = porcentaje_sobreprecio
tasa_financiacion_mensual = (((precio_cuotas/precio_contado) ** (1/cantidad_cuotas)) - 1)

# Crear DataFrame con el flujo de cuotas
meses = list(range(1, cantidad_cuotas + 1))
df_cuotas = pd.DataFrame({
    'Mes': meses,
    'Cuota Nominal': [valor_cuota] * cantidad_cuotas,
    'Inflación Acumulada': [(1 + inflacion_mensual) ** mes for mes in meses],
    'Cuota Real (Valor Actual)': [valor_cuota / ((1 + inflacion_mensual) ** mes) for mes in meses]
})

# Calcular VAN de las cuotas
van_cuotas = df_cuotas['Cuota Real (Valor Actual)'].sum()

# Layout principal - dividir en columnas
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📈 Análisis de la Financiación")
    
    # Métricas principales
    col1_1, col1_2, col1_3 = st.columns(3)
    
    with col1_1:
        st.metric(
            label="Sobreprecio",
            value=f"${sobreprecio:,.0f}",
            delta=f"{porcentaje_sobreprecio:.1f}%"
        )
    
    with col1_2:
        st.metric(
            label="Valor de cada cuota",
            value=f"${valor_cuota:,.0f}",
            delta=f"{cantidad_cuotas} cuotas"
        )
    
    with col1_3:
        st.metric(
            label="Tasa mensual",
            value=f"{tasa_financiacion_mensual*100:.2f}%",
            delta=f"vs inflación {inflacion_mensual*100:.1f}%"
        )

with col2:
    st.header("💡 Análisis con Inflación")
    
    # Métricas de inflación
    col2_1, col2_2, col2_3 = st.columns(3)
    
    with col2_1:
        st.metric(
            label="Valor real total cuotas",
            value=f"${van_cuotas:,.0f}",
            delta=f"{((van_cuotas-precio_contado)/precio_contado)*100:.1f}%",
            delta_color="inverse"
        )
    
    with col2_2:
        ahorro_inflacion = precio_cuotas - van_cuotas
        st.metric(
            label="'Ahorro' por inflación",
            value=f"${ahorro_inflacion:,.0f}",
            help="Cuánto menos pagas en términos reales por la inflación"
        )
    
    with col2_3:
        diferencia_real = van_cuotas - precio_contado
        st.metric(
            label="Diferencia real",
            value=f"${abs(diferencia_real):,.0f}",
            delta="Conviene cuotas" if van_cuotas < precio_contado else "Conviene contado",
            delta_color="normal" if van_cuotas < precio_contado else "inverse"
        )

# Separador
st.divider()

# Gráficos
col3, col4 = st.columns([1, 1])

with col3:
    st.subheader("📊 Evolución del valor real de las cuotas")
    
    # Gráfico de barras con valor nominal vs real
    fig_cuotas = go.Figure()
    
    fig_cuotas.add_trace(go.Bar(
        x=df_cuotas['Mes'],
        y=df_cuotas['Cuota Nominal'],
        name='Cuota Nominal',
        marker_color='lightblue',
        opacity=0.7
    ))
    
    fig_cuotas.add_trace(go.Bar(
        x=df_cuotas['Mes'],
        y=df_cuotas['Cuota Real (Valor Actual)'],
        name='Valor Real (ajustado por inflación)',
        marker_color='darkblue'
    ))
    
    fig_cuotas.update_layout(
        xaxis_title="Mes",
        yaxis_title="Valor ($)",
        hovermode='x unified',
        showlegend=True,
        height=400
    )
    
    st.plotly_chart(fig_cuotas, use_container_width=True)

with col4:
    st.subheader("📈 Comparación acumulada")
    
    # Gráfico de líneas con el costo acumulado
    df_cuotas['Pago Acumulado Nominal'] = df_cuotas['Cuota Nominal'].cumsum()
    df_cuotas['Pago Acumulado Real'] = df_cuotas['Cuota Real (Valor Actual)'].cumsum()
    
    fig_acumulado = go.Figure()
    
    fig_acumulado.add_trace(go.Scatter(
        x=df_cuotas['Mes'],
        y=df_cuotas['Pago Acumulado Nominal'],
        mode='lines+markers',
        name='Pago Acumulado Nominal',
        line=dict(color='red', width=2)
    ))
    
    fig_acumulado.add_trace(go.Scatter(
        x=df_cuotas['Mes'],
        y=df_cuotas['Pago Acumulado Real'],
        mode='lines+markers',
        name='Pago Acumulado Real',
        line=dict(color='green', width=2)
    ))
    
    fig_acumulado.add_hline(
        y=precio_contado,
        line_dash="dash",
        line_color="gray",
        annotation_text="Precio Contado"
    )
    
    fig_acumulado.update_layout(
        xaxis_title="Mes",
        yaxis_title="Monto Acumulado ($)",
        hovermode='x unified',
        showlegend=True,
        height=400
    )
    
    st.plotly_chart(fig_acumulado, use_container_width=True)

# Análisis de inversión alternativa
if considerar_inversion:
    st.divider()
    st.header("💼 Análisis con Inversión Alternativa")
    
    # Calcular el rendimiento de invertir el precio de contado
    monto_invertido = precio_contado
    rendimientos = []
    saldo_inversion = precio_contado
    
    for mes in range(1, cantidad_cuotas + 1):
        # Ganar intereses
        saldo_inversion = saldo_inversion * (1 + tasa_inversion)
        # Pagar la cuota
        saldo_inversion -= valor_cuota
        rendimientos.append(saldo_inversion)
    
    col5, col6 = st.columns([1, 2])
    
    with col5:
        saldo_final = rendimientos[-1]
        ganancia_inversion = saldo_final if saldo_final > 0 else 0
        
        st.metric(
            label="Saldo final si inviertes",
            value=f"${saldo_final:,.0f}",
            delta="Ganancia" if saldo_final > 0 else "Pérdida",
            delta_color="normal" if saldo_final > 0 else "inverse"
        )
        
        if saldo_final > 0:
            st.success(f"💰 Si inviertes el dinero y pagas las cuotas, te quedarían ${saldo_final:,.0f}")
        else:
            st.warning(f"⚠️ Necesitarías ${abs(saldo_final):,.0f} adicionales")
    
    with col6:
        # Gráfico de evolución de la inversión
        fig_inversion = go.Figure()
        
        fig_inversion.add_trace(go.Scatter(
            x=list(range(1, cantidad_cuotas + 1)),
            y=rendimientos,
            mode='lines+markers',
            name='Saldo de inversión',
            fill='tozeroy',
            line=dict(color='purple', width=2)
        ))
        
        fig_inversion.add_hline(
            y=0,
            line_dash="dash",
            line_color="red"
        )
        
        fig_inversion.update_layout(
            title="Evolución del saldo si inviertes y pagas cuotas",
            xaxis_title="Mes",
            yaxis_title="Saldo ($)",
            height=300
        )
        
        st.plotly_chart(fig_inversion, use_container_width=True)

# Recomendación final
st.divider()
st.header("🎯 Recomendación")

# Análisis de conveniencia
# La decisión debe basarse en el VAN: si VAN < precio_contado, convienen las cuotas
beneficio_cuotas = precio_contado - van_cuotas
conviene_cuotas = van_cuotas < precio_contado

# Mostrar nota explicativa si hay discrepancia
if (tasa_financiacion_mensual < inflacion_mensual) and not conviene_cuotas:
    st.info("""
    **📌 Nota importante:** Aunque la tasa de financiación (%.2f%%) es menor que la inflación (%.1f%%), 
    el sobreprecio inicial es tan alto (%.1f%%) que la inflación no alcanza a compensarlo completamente. 
    Por eso el valor presente de las cuotas sigue siendo mayor que el precio de contado.
    """ % (tasa_financiacion_mensual*100, inflacion_mensual*100, porcentaje_sobreprecio))

# Crear el mensaje de recomendación
if conviene_cuotas:
    st.success("### ✅ Te conviene comprar en CUOTAS")
    st.markdown(f"""
    **Razones principales:**
    - En términos reales, pagarás ${van_cuotas:,.0f} en lugar de ${precio_cuotas:,.0f}
    - El valor presente de las cuotas (${van_cuotas:,.0f}) es menor que el precio de contado (${precio_contado:,.0f})
    - La inflación "licúa" ${ahorro_inflacion:,.0f} del costo de financiación
    - Ahorras ${abs(beneficio_cuotas):,.0f} en términos reales
    - Mantienes liquidez para emergencias o inversiones
    """)
else:
    st.warning("### ⚠️ Te conviene comprar de CONTADO")
    st.markdown(f"""
    **Razones principales:**
    - El valor presente de las cuotas (${van_cuotas:,.0f}) es mayor que el precio de contado (${precio_contado:,.0f})
    - Pagarías ${abs(diferencia_real):,.0f} adicionales en términos reales
    - Aunque la inflación ayuda, no compensa completamente el sobreprecio
    - La tasa efectiva después de inflación sigue siendo positiva
    """)

# Tabla resumen
st.subheader("📋 Resumen Comparativo")

resumen_data = {
    'Concepto': ['Pago Total', 'Valor Presente', 'Tasa Mensual', 'Conveniencia'],
    'Contado': [
        f"${precio_contado:,.0f}",
        f"${precio_contado:,.0f}",
        "0%",
        "✅" if not conviene_cuotas else "❌"
    ],
    'Cuotas': [
        f"${precio_cuotas:,.0f}",
        f"${van_cuotas:,.0f}",
        f"{tasa_financiacion_mensual*100:.2f}%",
        "✅" if conviene_cuotas else "❌"
    ],
    'Diferencia': [
        f"${sobreprecio:,.0f} ({porcentaje_sobreprecio:.1f}%)",
        f"${abs(diferencia_real):,.0f} ({'a favor de cuotas' if conviene_cuotas else 'a favor de contado'})",
        f"{tasa_financiacion_mensual*100:.2f}% vs {inflacion_mensual*100:.1f}% inflación",
        f"{'Ahorro' if conviene_cuotas else 'Costo extra'}: ${abs(beneficio_cuotas):,.0f}"
    ]
}

df_resumen = pd.DataFrame(resumen_data)
st.table(df_resumen)

# Footer con explicación
with st.expander("ℹ️ ¿Cómo funciona el cálculo?"):
    st.markdown("""
    ### Metodología:
    
    1. **Valor Presente de las cuotas**: Cada cuota futura se descuenta por la inflación para obtener su valor en pesos de hoy
    2. **Tasa de financiación**: Se calcula la tasa mensual implícita en el financiamiento
    3. **Comparación**: Se compara el valor presente total de las cuotas contra el precio de contado
    4. **Inversión alternativa** (opcional): Evalúa si es mejor invertir el dinero y pagar las cuotas con los rendimientos
    
    ### Fórmula del Valor Presente:
    ```
    VP = Cuota / (1 + inflación)^mes
    VAN = Suma de todos los VP
    ```
    
    ### ¿Por qué a veces conviene contado aunque la tasa < inflación?
    
    Aunque la tasa de financiación sea menor que la inflación, el **sobreprecio inicial puede ser tan alto** 
    que ni siquiera la inflación logra compensarlo completamente. Por eso es crucial calcular el valor 
    presente neto (VAN) de todas las cuotas y compararlo con el precio de contado.
    
    **Regla de decisión:**
    - Si VAN < Precio Contado → Convienen las cuotas
    - Si VAN > Precio Contado → Conviene contado
    
    ### Consideraciones:
    - Este análisis asume inflación constante (en la realidad varía)
    - No considera otros costos como seguros o gastos administrativos
    - La decisión final también depende de tu situación financiera personal
    """)

# Agregar un disclaimer
st.info("""
**Disclaimer:** Esta calculadora es una herramienta de análisis financiero con fines educativos. 
La decisión final debe considerar tu situación financiera personal, tolerancia al riesgo y otros factores no contemplados aquí.
""")
