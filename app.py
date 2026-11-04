import math
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title='ConcreteLab | Projeto A3', page_icon='🏗️', layout='wide')

st.title('🏗️ ConcreteLab')
st.subheader('Otimização geométrica de reservatórios de concreto')
st.caption('Projeto A3 | Engenharia Civil + Engenharia de Software | Modelo didático, não estrutural')

with st.sidebar:
    st.header('Parâmetros do projeto')
    capacidade = st.number_input('Capacidade interna (m³)', min_value=1.0, max_value=1000.0, value=12.0, step=1.0)
    espessura_cm = st.slider('Espessura uniforme (cm)', min_value=5, max_value=30, value=15, step=1)
    lado = st.slider('Lado interno da base (m)', min_value=1.0, max_value=10.0, value=2.50, step=0.05)
    st.info('Hipóteses: base interna quadrada, reservatório sem tampa, paredes e base de espessura uniforme, sem armaduras ou verificação de resistência.')

t = espessura_cm / 100
V = capacidade

def consumo(x):
    h = V / x**2
    return (x + 2*t)**2 * (h + t) - V

x_otimo = (2*V)**(1/3)
h_otima = V / x_otimo**2
h = V / lado**2
c_atual = consumo(lado)
c_otimo = consumo(x_otimo)
economia = max(0.0, 100*(c_atual-c_otimo)/c_atual)

def derivada(x):
    return t*(2*x + 4*t - 4*V/x**2 - 8*t*V/x**3)

def segunda_derivada(x):
    return t*(2 + 8*V/x**3 + 24*t*V/x**4)

st.markdown('### Indicadores')
a,b,c,d = st.columns(4)
a.metric('Consumo atual', f'{c_atual:.3f} m³')
b.metric('Consumo mínimo', f'{c_otimo:.3f} m³')
c.metric('Economia geométrica', f'{economia:.1f}%')
d.metric('Lado ótimo', f'{x_otimo:.3f} m')

st.markdown('### 1. Curva de otimização')
# Domínio exibido inclui sempre a geometria escolhida e a ótima.
x_min = max(0.5, min(lado, x_otimo)*0.5)
x_max = max(lado, x_otimo)*1.8
xs = [x_min + (x_max-x_min)*i/249 for i in range(250)]
ys = [consumo(x) for x in xs]
fig = go.Figure()
fig.add_trace(go.Scatter(x=xs, y=ys, mode='lines', name='Consumo de concreto', line=dict(color='#38A6E6', width=3)))
fig.add_trace(go.Scatter(x=[lado], y=[c_atual], mode='markers', name='Geometria escolhida', marker=dict(color='#F59E0B', size=12)))
fig.add_trace(go.Scatter(x=[x_otimo], y=[c_otimo], mode='markers', name='Mínimo matemático', marker=dict(color='#22C55E', size=13, symbol='diamond')))
fig.update_layout(xaxis_title='Lado interno da base (m)', yaxis_title='Volume geométrico de concreto (m³)', hovermode='x unified', height=410, margin=dict(l=20,r=20,t=20,b=20))
st.plotly_chart(fig, use_container_width=True)

st.markdown('### 2. Comparação de geometrias')
col1,col2 = st.columns(2)
with col1:
    st.markdown('**Geometria escolhida**')
    st.write(f'Base interna: **{lado:.3f} × {lado:.3f} m**')
    st.write(f'Altura interna: **{h:.3f} m**')
    st.write(f'Concreto: **{c_atual:.3f} m³**')
with col2:
    st.markdown('**Geometria ótima no modelo**')
    st.write(f'Base interna: **{x_otimo:.3f} × {x_otimo:.3f} m**')
    st.write(f'Altura interna: **{h_otima:.3f} m**')
    st.write(f'Concreto: **{c_otimo:.3f} m³**')

comparacao = go.Figure(go.Bar(x=['Escolhida','Ótima'], y=[c_atual,c_otimo], marker_color=['#F59E0B','#22C55E'], text=[f'{c_atual:.3f}',f'{c_otimo:.3f}'], textposition='auto'))
comparacao.update_layout(yaxis_title='Concreto (m³)', height=300, margin=dict(l=20,r=20,t=20,b=20))
st.plotly_chart(comparacao, use_container_width=True)

with st.expander('3. Fundamentação matemática e verificação do mínimo', expanded=True):
    st.latex(r'V=x^2h\quad\Rightarrow\quad h=\frac{V}{x^2}')
    st.latex(r'C(x)=(x+2t)^2\left(\frac{V}{x^2}+t\right)-V')
    st.latex(r'C\prime(x)=t\left(2x+4t-\frac{4V}{x^2}-\frac{8tV}{x^3}\right)')
    st.latex(r'C\prime(x)=0\quad\Rightarrow\quad (x+2t)(x^3-2V)=0')
    st.latex(r'x_{\mathrm{otimo}}=\sqrt[3]{2V}')
    st.latex(r'C\prime\prime(x)=t\left(2+\frac{8V}{x^3}+\frac{24tV}{x^4}\right)>0')
    st.write(f'No ponto ótimo, C\'(x) = **{derivada(x_otimo):.8f} m²** e C\'\'(x) = **{segunda_derivada(x_otimo):.4f} m** (positivo).')
    st.caption('A convexidade para x>0 demonstra mínimo global neste modelo geométrico sem restrições adicionais.')

st.markdown('### 4. Cenários para o artigo científico')
cenarios=[]
for cap in [6.0,12.0,24.0]:
    xo=(2*cap)**(1/3)
    ho=cap/xo**2
    co=(xo+2*t)**2*(ho+t)-cap
    cenarios.append({'Capacidade (m³)':cap,'Lado ótimo (m)':round(xo,3),'Altura ótima (m)':round(ho,3),'Concreto mínimo (m³)':round(co,3)})
df=pd.DataFrame(cenarios)
st.dataframe(df, use_container_width=True, hide_index=True)
st.download_button('Baixar resultados (CSV)', data=df.to_csv(index=False).encode('utf-8-sig'), file_name='concretelab_cenarios.csv', mime='text/csv')

st.warning('Uso acadêmico: esta ferramenta estima volumes geométricos, NÃO dimensiona reservatórios. Não considera pressão hidrostática, armaduras, fissuração, impermeabilização, cargas, custos ou normas estruturais. A geometria ótima matemática pode não ser construtivamente adequada.')
