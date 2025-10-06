# app.py - Analisador de Texto Multidimensional
# Referência Teórica: Russell, S. J., & Norvig, P. (2020). 
# Artificial Intelligence: A Modern Approach (4th ed.). Pearson.
# André Luiz Rocha - 06/10/2025 - 10:32

import streamlit as st
import re
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

# Definição de categorias universais baseadas na adaptação do framework de Russell & Norvig
categories = {
    "Pensamento Subjetivo": [
        "acredito", "penso", "sinto", "acho", "imagino", "sonho", "desejo",
        "emoção", "sentimento", "intuição", "criatividade", "inspiração",
        "paixão", "medo", "alegria", "tristeza", "amor", "esperança", "fé",
        "consciência", "percepção", "sensação", "vontade", "motivação",
        "opinião", "perspectiva", "visão", "impressão"
    ],
    "Pensamento Objetivo": [
        "dados", "fatos", "evidências", "estudo", "pesquisa", "análise",
        "lógica", "razão", "racional", "científico", "estatística", "prova",
        "teoria", "hipótese", "método", "sistema", "estrutura", "princípio",
        "lei", "regra", "padrão", "objetivo", "imparcial", "neutralidade",
        "verdade", "comprovação", "validação", "experimento"
    ],
    "Ação Comportamental": [
        "comportamento", "ação", "atitude", "decisão", "escolha", "reação",
        "interação", "comunicação", "diálogo", "conversa", "expressão",
        "relacionamento", "cooperação", "colaboração", "confronto", "resposta",
        "gesto", "postura", "conduta", "procedimento", "iniciativa",
        "social", "convivência", "empatia", "diplomacia"
    ],
    "Ação Prática": [
        "execução", "implementação", "aplicação", "realização", "produção",
        "construção", "desenvolvimento", "criação", "fabricação", "operacional",
        "prático", "concreto", "resultado", "efeito", "impacto", "performance",
        "eficácia", "eficiência", "produtividade", "solução", "resolução",
        "projeto", "tarefa", "meta", "objetivo", "planejamento"
    ]
}

# Título e descrição
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
        
        # Análise de sentimento com TextBlob
        try:
            blob = TextBlob(texto)
            # Tentar traduzir para melhor análise se for português
            if any(palavra in texto.lower() for palavra in ['é', 'á', 'ã', 'ç', 'õ']):
                texto_ingles = str(blob.translate(to='en'))
                blob = TextBlob(texto_ingles)
        except:
            blob = TextBlob(texto)  # Usar original se tradução falhar
            
        sentiment = blob.sentiment
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            polarity = sentiment.polarity
            if polarity > 0.1:
                emoji = "😊"
                status = "Positivo"
            elif polarity < -0.1:
                emoji = "😞"
                status = "Negativo"
            else:
                emoji = "😐"
                status = "Neutro"
            
            st.metric(f"Polaridade {emoji}", f"{polarity:.3f}", status)
        
        with col2:
            subjectivity = sentiment.subjectivity
            if subjectivity > 0.6:
                nivel = "Alta"
            elif subjectivity > 0.3:
                nivel = "Média"
            else:
                nivel = "Baixa"
            st.metric("Subjetividade", f"{subjectivity:.3f}", nivel)
        
        with col3:
            palavras_count = len(texto.split())
            st.metric("📝 Palavras", palavras_count)
        
        # Barra de sentimento visual
        st.markdown(f"""
        <div style="background: #ecf0f1; border-radius: 10px; padding: 5px; margin: 10px 0;">
            <div style="background: linear-gradient(90deg, #e74c3c 0%, #f39c12 50%, #2ecc71 100%); 
                        border-radius: 8px; padding: 10px; text-align: center; color: white; font-weight: bold;
                        width: {((polarity + 1) / 2) * 100}%">
                Sentimento: {polarity:.3f} ({status})
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. ANÁLISE DOS EIXOS CONCEITUAIS
        st.header("🎯 Análise dos Eixos Conceituais")
        
        # Processamento do texto
        texto_limpo = re.sub(r'[^\w\s]', '', texto.lower())
        
        # Inicializar scores para todas as categorias
        scores = {categoria: 0 for categoria in categories.keys()}
        total_palavras_chave = 0
        
        # Contagem de ocorrências
        for categoria, palavras_chave in categories.items():
            for palavra in palavras_chave:
                pattern = r'\b' + re.escape(palavra) + r'\b'
                matches = re.findall(pattern, texto_limpo)
                scores[categoria] += len(matches)
                total_palavras_chave += len(matches)
        
        # Cálculo de percentuais
        total_score = sum(scores.values())
        percentuais = {}
        
        for categoria, score in scores.items():
            if total_score > 0:
                percentuais[categoria] = (score / total_score) * 100
            else:
                percentuais[categoria] = 0

        # Cálculo dos eixos principais
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

        # Exibição dos eixos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🧠 Eixo Pensamento vs Ação")
            
            # Métricas
            progresso_pensamento = pensamento_percent / 100
            progresso_acao = acao_percent / 100
            
            st.markdown(f"**Pensamento**: {pensamento_percent:.1f}%")
            st.progress(progresso_pensamento)
            
            st.markdown(f"**Ação**: {acao_percent:.1f}%")
            st.progress(progresso_acao)
            
            # Gráfico de pizza
            fig1, ax1 = plt.subplots(figsize=(6, 6))
            cores = ['#3498db', '#e74c3c']
            ax1.pie([pensamento_percent, acao_percent], 
                   labels=[f'Pensamento\n{pensamento_percent:.1f}%', f'Ação\n{acao_percent:.1f}%'],
                   colors=cores, autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')
            st.pyplot(fig1)
        
        with col2:
            st.subheader("📊 Eixo Subjetivo vs Objetivo")
            
            # Métricas
            progresso_subjetivo = subjetivo_percent / 100
            progresso_objetivo = objetivo_percent / 100
            
            st.markdown(f"**Subjetivo**: {subjetivo_percent:.1f}%")
            st.progress(progresso_subjetivo)
            
            st.markdown(f"**Objetivo**: {objetivo_percent:.1f}%")
            st.progress(progresso_objetivo)
            
            # Gráfico de pizza
            fig2, ax2 = plt.subplots(figsize=(6, 6))
            cores = ['#9b59b6', '#2ecc71']
            ax2.pie([subjetivo_percent, objetivo_percent], 
                   labels=[f'Subjetivo\n{subjetivo_percent:.1f}%', f'Objetivo\n{objetivo_percent:.1f}%'],
                   colors=cores, autopct='%1.1f%%', startangle=90)
            ax2.axis('equal')
            st.pyplot(fig2)

        # 3. MATRIZ CONCEITUAL COMPLETA
        st.header("🎯 Matriz Conceitual Completa")
        
        matriz_html = f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0;">
            <div style="background: linear-gradient(135deg, #e8f4fd, #b3d9ff); padding: 20px; border-radius: 10px; text-align: center; border: 2px solid #3498db;">
                <h4>🧠 Pensamento</h4>
                <h5>Subjetivo</h5>
                <div style="font-size: 28px; font-weight: bold; color: #3498db;">{percentuais['Pensamento Subjetivo']:.1f}%</div>
                <small>Emoções, intuições, sentimentos</small>
            </div>
            <div style="background: linear-gradient(135deg, #e6f7e9, #99e699); padding: 20px; border-radius: 10px; text-align: center; border: 2px solid #2ecc71;">
                <h4>🧠 Pensamento</h4>
                <h5>Objetivo</h5>
                <div style="font-size: 28px; font-weight: bold; color: #2ecc71;">{percentuais['Pensamento Objetivo']:.1f}%</div>
                <small>Dados, lógica, fatos</small>
            </div>
            <div style="background: linear-gradient(135deg, #fff0f0, #ffb3b3); padding: 20px; border-radius: 10px; text-align: center; border: 2px solid #e74c3c;">
                <h4>⚡ Ação</h4>
                <h5>Comportamental</h5>
                <div style="font-size: 28px; font-weight: bold; color: #e74c3c;">{percentuais['Ação Comportamental']:.1f}%</div>
                <small>Interações, relações, comunicação</small>
            </div>
            <div style="background: linear-gradient(135deg, #fcf8e3, #ffe680); padding: 20px; border-radius: 10px; text-align: center; border: 2px solid #f39c12;">
                <h4>⚡ Ação</h4>
                <h5>Prática</h5>
                <div style="font-size: 28px; font-weight: bold; color: #f39c12;">{percentuais['Ação Prática']:.1f}%</div>
                <small>Execução, resultados, eficiência</small>
            </div>
        </div>
        """
        st.markdown(matriz_html, unsafe_allow_html=True)

        # 4. INTERPRETAÇÃO E INSIGHTS
        st.header("💡 Insights e Interpretação")
        
        insights = []
        
        # Insights baseados nos eixos
        if pensamento_percent > 70:
            insights.append("🧠 **Texto reflexivo**: Predominância de elementos de pensamento e análise")
        elif acao_percent > 70:
            insights.append("⚡ **Texto ativo**: Foco em ações, comportamentos e resultados")
        else:
            insights.append("⚖️ **Equilíbrio reflexão-ação**: Balanceamento entre pensar e agir")
        
        if subjetivo_percent > 70:
            insights.append("🎭 **Abordagem subjetiva**: Ênfase em experiências pessoais, emoções e perspectivas individuais")
        elif objetivo_percent > 70:
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
        
        for insight in insights:
            st.info(insight)

        # 5. RESUMO ESTATÍSTICO
        with st.expander("📋 Resumo Estatístico Detalhado"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Distribuição por Categoria")
                dados_categorias = {
                    'Categoria': list(percentuais.keys()),
                    'Percentual': list(percentuais.values()),
                    'Ocorrências': list(scores.values())
                }
                df_categorias = pd.DataFrame(dados_categorias)
                st.dataframe(df_categorias, use_container_width=True)
            
            with col2:
                st.subheader("Métricas de Texto")
                metricas = {
                    'Metrica': ['Total de Palavras', 'Palavras-chave Encontradas', 'Densidade de Palavras-chave', 
                               'Sentimento', 'Subjetividade'],
                    'Valor': [palavras_count, total_palavras_chave, 
                             f"{(total_palavras_chave/palavras_count*100):.1f}%" if palavras_count > 0 else "0%",
                             f"{polarity:.3f}", f"{subjectivity:.3f}"]
                }
                df_metricas = pd.DataFrame(metricas)
                st.dataframe(df_metricas, use_container_width=True)
            
            st.subheader("Exemplos de Palavras Encontradas")
            palavras_encontradas = []
            for categoria, palavras_chave in categories.items():
                encontradas = [palavra for palavra in palavras_chave if re.search(r'\b' + palavra + r'\b', texto_limpo)]
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

# Sidebar com informações
with st.sidebar:
    st.header("🎯 Sobre a Análise")
    st.markdown("""
    **Eixos Analisados:**
    
    🧠 **Pensamento vs Ação**
    - Reflexão teórica versus implementação prática
    
    📊 **Subjetivo vs Objetivo**
    - Experiências pessoais versus fatos mensuráveis
    
    **Aplicações:**
    - Análise de discursos
    - Avaliação de tom de comunicação  
    - Estilo de escrita
    - Perfil argumentativo
    - Análise de conteúdo
    """)
    
    # Referência Bibliográfica
    with st.expander("📚 Referência Bibliográfica"):
        st.markdown("""
        **Base Teórica:**
        
        Este sistema é inspirado na classificação de Inteligência Artificial proposta por:
        
        **Russell, S. J., & Norvig, P. (2020). Artificial Intelligence: A Modern Approach (4th ed.). Pearson.**
        
        No livro, os autores categorizam a IA em quatro abordagens principais:
        - Pensar como humano
        - Agir como humano  
        - Pensar racionalmente
        - Agir racionalmente
        
        Adaptamos essas categorias para uma análise textual geral, mapeando para:
        - Pensamento Subjetivo (humano) vs Objetivo (racional)
        - Ação Comportamental (humana) vs Prática (racional)
        """)
    
    st.header("🔧 Instalação")
    st.markdown("""
    ```bash
    pip install streamlit textblob matplotlib pandas
    python -m textblob.download_corpora
    ```
    """)

# Informações gerais
st.sidebar.markdown("---")
st.sidebar.info("""
**📝 Como usar:**
1. Cole qualquer texto na área de entrada
2. Clique em "Analisar Texto"
3. Explore os diferentes tipos de análise

**🔍 Aplicável a:**
- Artigos e notícias
- Discursos e apresentações
- Redações e textos acadêmicos
- Conteúdo de marketing
- Análise de comunicação corporativa
""")
