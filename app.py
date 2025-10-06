# app.py - Analisador de Texto Multidimensional
# Referência Teórica: Russell, S. J., & Norvig, P. (2020). 
# Artificial Intelligence: A Modern Approach (4th ed.). Pearson.
# André Luiz Rocha

import streamlit as st
import re
import json
from collections import defaultdict
from textblob import TextBlob
import matplotlib.pyplot as plt
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Analisador de Texto Multidimensional",
    page_icon="🧠",
    layout="wide"
)

# Carregar CSS personalizado
def load_css():
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# Carregar categorias do JSON
@st.cache_data
def load_categories():
    with open('categories.json', 'r', encoding='utf-8') as f:
        return json.load(f)

categories = load_categories()

# Funções de análise
def analyze_sentiment(texto):
    """Analisa o sentimento do texto"""
    try:
        blob = TextBlob(texto)
        if any(palavra in texto.lower() for palavra in ['é', 'á', 'ã', 'ç', 'õ']):
            texto_ingles = str(blob.translate(to='en'))
            blob = TextBlob(texto_ingles)
    except:
        blob = TextBlob(texto)
    return blob.sentiment

def analyze_categories(texto, categories):
    """Analisa as categorias no texto"""
    texto_limpo = re.sub(r'[^\w\s]', '', texto.lower())
    scores = {categoria: 0 for categoria in categories.keys()}
    total_palavras_chave = 0
    
    for categoria, palavras_chave in categories.items():
        for palavra in palavras_chave:
            pattern = r'\b' + re.escape(palavra) + r'\b'
            matches = re.findall(pattern, texto_limpo)
            scores[categoria] += len(matches)
            total_palavras_chave += len(matches)
    
    return scores, total_palavras_chave

def calculate_percentages(scores):
    """Calcula percentuais baseados nos scores"""
    total_score = sum(scores.values())
    percentuais = {}
    
    for categoria, score in scores.items():
        if total_score > 0:
            percentuais[categoria] = (score / total_score) * 100
        else:
            percentuais[categoria] = 0
    
    return percentuais

def calculate_axes(percentuais):
    """Calcula os eixos conceituais"""
    pensamento_total = percentuais['Pensamento Subjetivo'] + percentuais['Pensamento Objetivo']
    acao_total = percentuais['Ação Comportamental'] + percentuais['Ação Prática']
    
    subjetividade_total = percentuais['Pensamento Subjetivo'] + percentuais['Ação Comportamental']
    objetividade_total = percentuais['Pensamento Objetivo'] + percentuais['Ação Prática']
    
    # Normalizar para 100% cada eixo
    if pensamento_total + acao_total > 0:
        pensamento_percent = (pensamento_total / (pensamento_total + acao_total)) * 100
        acao_percent = (acao_total / (pensamento_total + acao_total)) * 100
    else:
        pensamento_percent = acao_percent = 50
        
    if subjetividade_total + objetividade_total > 0:
        subjetivo_percent = (subjetividade_total / (subjetividade_total + objetividade_total)) * 100
        objetivo_percent = (objetividade_total / (subjetividade_total + objetividade_total)) * 100
    else:
        subjetivo_percent = objetivo_percent = 50
    
    return {
        'pensamento': pensamento_percent,
        'acao': acao_percent,
        'subjetivo': subjetivo_percent,
        'objetivo': objetivo_percent
    }

def generate_insights(polarity, subjectivity, axes):
    """Gera insights baseados na análise"""
    insights = []
    
    # Insights baseados nos eixos
    if axes['pensamento'] > 70:
        insights.append("🧠 **Texto reflexivo**: Predominância de elementos de pensamento e análise")
    elif axes['acao'] > 70:
        insights.append("⚡ **Texto ativo**: Foco em ações, comportamentos e resultados")
    else:
        insights.append("⚖️ **Equilíbrio reflexão-ação**: Balanceamento entre pensar e agir")
    
    if axes['subjetivo'] > 70:
        insights.append("🎭 **Abordagem subjetiva**: Ênfase em experiências pessoais, emoções e perspectivas individuais")
    elif axes['objetivo'] > 70:
        insights.append("📐 **Abordagem objetiva**: Foco em fatos, dados e análise imparcial")
    else:
        insights.append("🔄 **Perspectiva integrada**: Combina elementos subjetivos e objetivos")
    
    # Insights baseados no sentimento
    if polarity > 0.3:
        insights.append("✅ **Tom positivo**: Linguagem otimista e construtiva")
    elif polarity < -0.3:
        insights.append("⚠️ **Tom crítico**: Linguagem cautelosa ou negativa")
    else:
        insights.append("🔍 **Tom neutro**: Abordagem equilibrada e factual")
    
    # Insights baseados na subjetividade
    if subjectivity > 0.7:
        insights.append("💭 **Alta subjetividade**: Forte presença de opiniões e perspectivas pessoais")
    elif subjectivity < 0.3:
        insights.append("📊 **Baixa subjetividade**: Linguagem factual e impessoal")
    
    return insights

# Interface principal
st.title("Analisador de Texto Multidimensional")
st.subheader("Análise de Sentimento + Eixos Conceituais para Qualquer Texto")

# Entrada do usuário
texto = st.text_area("Digite o texto para análise:", height=200, 
                     placeholder="Cole ou digite aqui qualquer texto (artigos, discursos, redações, relatórios, etc.)...")

if st.button("Analisar Texto"):
    if not texto:
        st.warning("Por favor, insira um texto para análise.")
    else:
        # 1. ANÁLISE DE SENTIMENTO
        st.header("📊 Análise de Sentimento")
        
        sentiment = analyze_sentiment(texto)
        polarity = sentiment.polarity
        subjectivity = sentiment.subjectivity
        palavras_count = len(texto.split())
        
        # Métricas de sentimento
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if polarity > 0.1:
                emoji, status = "😊", "Positivo"
            elif polarity < -0.1:
                emoji, status = "😞", "Negativo"
            else:
                emoji, status = "😐", "Neutro"
            st.metric(f"Polaridade {emoji}", f"{polarity:.3f}", status)
        
        with col2:
            if subjectivity > 0.6:
                nivel = "Alta"
            elif subjectivity > 0.3:
                nivel = "Média"
            else:
                nivel = "Baixa"
            st.metric("Subjetividade", f"{subjectivity:.3f}", nivel)
        
        with col3:
            st.metric("📝 Palavras", palavras_count)
        
        # Barra de sentimento visual
        st.markdown(f"""
        <div class="sentiment-bar">
            <div class="sentiment-fill" style="width: {((polarity + 1) / 2) * 100}%">
                Sentimento: {polarity:.3f} ({status})
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. ANÁLISE DOS EIXOS CONCEITUAIS
        st.header("🎯 Análise dos Eixos Conceituais")
        
        scores, total_palavras_chave = analyze_categories(texto, categories)
        percentuais = calculate_percentages(scores)
        axes = calculate_axes(percentuais)

        # Exibição dos eixos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🧠 Eixo Pensamento vs Ação")
            st.markdown(f"**Pensamento**: {axes['pensamento']:.1f}%")
            st.progress(axes['pensamento'] / 100)
            st.markdown(f"**Ação**: {axes['acao']:.1f}%")
            st.progress(axes['acao'] / 100)
            
            # Gráfico de pizza
            fig1, ax1 = plt.subplots(figsize=(6, 6))
            ax1.pie([axes['pensamento'], axes['acao']], 
                   labels=[f'Pensamento\n{axes["pensamento"]:.1f}%', f'Ação\n{axes["acao"]:.1f}%'],
                   colors=['#3498db', '#e74c3c'], autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')
            st.pyplot(fig1)
        
        with col2:
            st.subheader("📊 Eixo Subjetivo vs Objetivo")
            st.markdown(f"**Subjetivo**: {axes['subjetivo']:.1f}%")
            st.progress(axes['subjetivo'] / 100)
            st.markdown(f"**Objetivo**: {axes['objetivo']:.1f}%")
            st.progress(axes['objetivo'] / 100)
            
            # Gráfico de pizza
            fig2, ax2 = plt.subplots(figsize=(6, 6))
            ax2.pie([axes['subjetivo'], axes['objetivo']], 
                   labels=[f'Subjetivo\n{axes["subjetivo"]:.1f}%', f'Objetivo\n{axes["objetivo"]:.1f}%'],
                   colors=['#9b59b6', '#2ecc71'], autopct='%1.1f%%', startangle=90)
            ax2.axis('equal')
            st.pyplot(fig2)

        # 3. MATRIZ CONCEITUAL COMPLETA
        st.header("🎯 Matriz Conceitual Completa")
        
        matriz_html = f"""
        <div class="concept-matrix">
            <div class="matrix-cell matrix-cell-subjective">
                <h4>🧠 Pensamento</h4>
                <h5>Subjetivo</h5>
                <div class="matrix-value">{percentuais['Pensamento Subjetivo']:.1f}%</div>
                <small>Emoções, intuições, sentimentos</small>
            </div>
            <div class="matrix-cell matrix-cell-objective">
                <h4>🧠 Pensamento</h4>
                <h5>Objetivo</h5>
                <div class="matrix-value">{percentuais['Pensamento Objetivo']:.1f}%</div>
                <small>Dados, lógica, fatos</small>
            </div>
            <div class="matrix-cell matrix-cell-behavioral">
                <h4>⚡ Ação</h4>
                <h5>Comportamental</h5>
                <div class="matrix-value">{percentuais['Ação Comportamental']:.1f}%</div>
                <small>Interações, relações, comunicação</small>
            </div>
            <div class="matrix-cell matrix-cell-practical">
                <h4>⚡ Ação</h4>
                <h5>Prática</h5>
                <div class="matrix-value">{percentuais['Ação Prática']:.1f}%</div>
                <small>Execução, resultados, eficiência</small>
            </div>
        </div>
        """
        st.markdown(matriz_html, unsafe_allow_html=True)

        # 4. INTERPRETAÇÃO E INSIGHTS
        st.header("💡 Insights e Interpretação")
        
        insights = generate_insights(polarity, subjectivity, axes)
        for insight in insights:
            st.info(insight)

        # 5. RESUMO ESTATÍSTICO
        with st.expander("📋 Resumo Estatístico Detalhado"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Distribuição por Categoria")
                df_categorias = pd.DataFrame({
                    'Categoria': list(percentuais.keys()),
                    'Percentual': list(percentuais.values()),
                    'Ocorrências': list(scores.values())
                })
                st.dataframe(df_categorias, use_container_width=True)
            
            with col2:
                st.subheader("Métricas de Texto")
                densidade = f"{(total_palavras_chave/palavras_count*100):.1f}%" if palavras_count > 0 else "0%"
                df_metricas = pd.DataFrame({
                    'Metrica': ['Total de Palavras', 'Palavras-chave Encontradas', 'Densidade de Palavras-chave', 
                               'Sentimento', 'Subjetividade'],
                    'Valor': [palavras_count, total_palavras_chave, densidade, f"{polarity:.3f}", f"{subjectivity:.3f}"]
                })
                st.dataframe(df_metricas, use_container_width=True)
            
            st.subheader("Exemplos de Palavras Encontradas")
            palavras_encontradas = []
            for categoria, palavras_chave in categories.items():
                encontradas = [palavra for palavra in palavras_chave if re.search(r'\b' + palavra + r'\b', texto.lower())]
                if encontradas:
                    palavras_encontradas.append(f"**{categoria}**: {', '.join(encontradas[:5])}" + 
                                              ("..." if len(encontradas) > 5 else ""))
            
            for item in palavras_encontradas:
                st.write(item)

        # 6. RECOMENDAÇÕES
        with st.expander("💎 Recomendações Baseadas na Análise"):
            st.markdown("""
            **Para comunicação eficaz baseada no perfil do texto:**
            
            - **Texto muito subjetivo**: Considere adicionar dados concretos para maior credibilidade
            - **Texto muito objetivo**: Pode beneficiar-se de elementos humanos e emocionais
            - **Foco excessivo em pensamento**: Inclua exemplos práticos e aplicações
            - **Foco excessivo em ação**: Desenvolva mais a fundamentação teórica
            - **Tom muito negativo**: Balance com aspectos positivos e soluções
            - **Tom muito positivo**: Inclua considerações sobre desafios e limitações
            """)

# Sidebar
with st.sidebar:
    st.header("🎯 Sobre a Análise")
    st.markdown("""
    <div class="sidebar-info">
    **Eixos Analisados:**
    
    🧠 **Pensamento vs Ação**
    - Reflexão teórica versus implementação prática
    
    📊 **Subjetivo vs Objetivo**
    - Experiências pessoais versus fatos mensuráveis
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📚 Referência Bibliográfica"):
        st.markdown("""
        **Base Teórica:**
        
        Este sistema é inspirado na classificação de Inteligência Artificial proposta por:
        
        **Russell, S. J., & Norvig, P. (2020). Artificial Intelligence: A Modern Approach (4th ed.). Pearson.**
        """)

st.sidebar.markdown("---")
st.sidebar.info("""
**📝 Como usar:**
1. Cole qualquer texto
2. Clique em "Analisar Texto"
3. Explore os resultados
""")
