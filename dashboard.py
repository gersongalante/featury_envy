import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from typing import Dict, List, Optional, Tuple
import json

# Importar funções do processador correto
from processador_correcto_parametros_longos_ou_feature_envy import (
    extrair_arquivo_aia,
    encontrar_arquivos_bky,
    parse_blockly_xml_to_ast as parse_blockly_xml,
    find_procedures_in_ast
)

# Configuração da página
st.set_page_config(
    page_title="Long Parameter List Detector",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header principal
    st.markdown('<h1 class="main-header">📋 Long Parameter List Detector</h1>', unsafe_allow_html=True)
    st.markdown("### Análise de Code Smells em Projetos App Inventor")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Parâmetros de análise
        st.subheader("Parâmetros de Análise")
        param_threshold = st.slider(
            "Limite de parâmetros",
            min_value=1,
            max_value=10,
            value=3,
            help="Número máximo de parâmetros permitidos antes de ser considerado um code smell"
        )
        
        st.markdown("---")
        st.markdown("### 📊 Sobre Long Parameter List")
        st.info("""
        **Long Parameter List** é um code smell que ocorre quando um método ou procedimento 
        tem muitos parâmetros, dificultando sua compreensão e manutenção.
        
        **Sintomas:**
        - Procedimento com muitos parâmetros (> 3-4)
        - Dificuldade em lembrar a ordem dos parâmetros
        - Código difícil de manter e testar
        - Violação do princípio de responsabilidade única
        """)
    
    # Área principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📁 Upload do Projeto")
        
        uploaded_file = st.file_uploader(
            "Selecione um arquivo .aia",
            type=['aia'],
            help="Arquivo de projeto do MIT App Inventor"
        )
        
        if uploaded_file is not None:
            # Mostrar informações do arquivo
            file_details = {
                "Nome": uploaded_file.name,
                "Tamanho": f"{uploaded_file.size / 1024:.2f} KB",
                "Tipo": uploaded_file.type
            }
            
            st.json(file_details)
            
            # Botão para iniciar análise
            if st.button("🚀 Iniciar Análise", type="primary"):
                with st.spinner("Analisando projeto..."):
                    results = analyze_project(uploaded_file, param_threshold)
                    display_results(results)
    
    with col2:
        st.header("📈 Estatísticas")
        
        if 'analysis_results' in st.session_state:
            results = st.session_state.analysis_results
            display_statistics(results)
        else:
            st.info("Faça upload de um arquivo .aia para ver as estatísticas")

def analyze_project(uploaded_file, param_threshold):
    """Analisa o projeto .aia e retorna os resultados"""
    
    # Criar diretório temporário
    with tempfile.TemporaryDirectory() as temp_dir:
        # Salvar arquivo temporário
        temp_file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_file_path, 'wb') as f:
            f.write(uploaded_file.getvalue())
        
        # Extrair arquivo .aia
        extracted_dir = os.path.join(temp_dir, "extracted")
        if not extrair_arquivo_aia(temp_file_path, extracted_dir):
            st.error("❌ Erro ao extrair arquivo .aia")
            return None
        
        # Encontrar arquivos .bky
        bky_files = encontrar_arquivos_bky(extracted_dir)
        if not bky_files:
            st.warning("⚠️ Nenhum arquivo .bky encontrado no projeto")
            return None
        
        # Analisar cada arquivo
        all_results = []
        total_screens = len(bky_files)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, bky_file in enumerate(bky_files):
            screen_name = os.path.basename(bky_file).replace('.bky', '')
            status_text.text(f"Analisando tela: {screen_name}")
            
            try:
                with open(bky_file, 'r', encoding='utf-8') as f:
                    xml_content = f.read()
                
                structured_data = parse_blockly_xml(xml_content)
                if structured_data:
                    # Detectar procedimentos
                    procedures = find_procedures_in_ast(structured_data)
                    
                    # Filtrar procedimentos com muitos parâmetros
                    smelly_procedures = [p for p in procedures if p['parameter_count'] > param_threshold]
                    
                    screen_result = {
                        'screen_name': screen_name,
                        'procedures': procedures,
                        'smelly_procedures': smelly_procedures,
                        'total_procedures': len(procedures),
                        'total_blocks': len(structured_data.get('blocks', []))
                    }
                    all_results.append(screen_result)
            
            except Exception as e:
                st.error(f"Erro ao analisar {screen_name}: {str(e)}")
            
            progress_bar.progress((i + 1) / total_screens)
        
        status_text.text("✅ Análise concluída!")
        
        # Salvar resultados na sessão
        st.session_state.analysis_results = all_results
        return all_results

def display_results(results):
    """Exibe os resultados da análise"""
    
    if not results:
        st.warning("Nenhum resultado encontrado")
        return
    
    # Métricas gerais
    total_screens = len(results)
    total_procedures = sum(screen.get('total_procedures', 0) for screen in results)
    total_smelly_procedures = sum(len(screen.get('smelly_procedures', [])) for screen in results)
    screens_with_smells = len([screen for screen in results if screen.get('smelly_procedures')])
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Telas Analisadas", total_screens)
    
    with col2:
        st.metric("Procedimentos Encontrados", total_procedures)
    
    with col3:
        st.metric("Procedimentos com Muitos Parâmetros", total_smelly_procedures)
    
    with col4:
        if total_screens > 0:
            percentage = (screens_with_smells / total_screens) * 100
            st.metric("Taxa de Problemas", f"{percentage:.1f}%")
        else:
            st.metric("Taxa de Problemas", "0%")
    
    # Resultados detalhados por tela
    st.header("📋 Resultados Detalhados")
    
    for screen_result in results:
        with st.expander(f"📱 {screen_result['screen_name']}", expanded=True):
            procedures = screen_result.get('procedures', [])
            smelly_procedures = screen_result.get('smelly_procedures', [])
            
            # Mostrar todos os procedimentos encontrados
            if procedures:
                st.info(f"📋 {len(procedures)} procedimento(s) encontrado(s) nesta tela")
                for proc in procedures:
                    is_smelly = proc['parameter_count'] > 3  # threshold padrão
                    if is_smelly:
                        st.warning(f"⚠️ **{proc['procedure_name']}** ({proc['parameter_count']} parâmetros)")
                    else:
                        st.success(f"✅ **{proc['procedure_name']}** ({proc['parameter_count']} parâmetros)")
                    
                    if proc['parameters']:
                        st.markdown(f"**Parâmetros:** {', '.join(proc['parameters'])}")
                    st.markdown("---")
            else:
                st.info("Nenhum procedimento encontrado nesta tela")
            
            # Mostrar casos problemáticos
            if smelly_procedures:
                st.error(f"🚨 {len(smelly_procedures)} procedimento(s) com muitos parâmetros encontrado(s)")
                
                for i, proc in enumerate(smelly_procedures, 1):
                    st.markdown(f"**Problema #{i}:** {proc['procedure_name']}")
                    
                    # Gráfico de parâmetros
                    fig = go.Figure(data=[
                        go.Bar(
                            x=['Parâmetros'],
                            y=[proc['parameter_count']],
                            marker_color=['#e74c3c']
                        )
                    ])
                    
                    fig.update_layout(
                        title=f"Parâmetros - {proc['procedure_name']}",
                        yaxis_title="Número de Parâmetros",
                        height=300
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Detalhes dos parâmetros
                    if proc['parameters']:
                        st.markdown("**Parâmetros:**")
                        for param in proc['parameters']:
                            st.markdown(f"- {param}")
                    
                    st.markdown("---")

def display_statistics(results):
    """Exibe estatísticas gerais"""
    
    if not results:
        return
    
    # Calcular estatísticas
    total_smelly_procedures = sum(len(screen.get('smelly_procedures', [])) for screen in results)
    screens_with_smells = len([screen for screen in results if screen.get('smelly_procedures')])
    total_screens = len(results)
    
    # Gráfico de pizza - Telas com/sem problemas
    fig_pie = px.pie(
        values=[screens_with_smells, total_screens - screens_with_smells],
        names=['Com Problemas', 'Sem Problemas'],
        title="Distribuição de Telas",
        color_discrete_sequence=['#e74c3c', '#2ecc71']
    )
    
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Gráfico de barras - Procedimentos problemáticos por tela
    screen_names = [screen['screen_name'] for screen in results]
    smelly_counts = [len(screen.get('smelly_procedures', [])) for screen in results]
    
    fig_bar = px.bar(
        x=screen_names,
        y=smelly_counts,
        title="Procedimentos com Muitos Parâmetros por Tela",
        labels={'x': 'Tela', 'y': 'Procedimentos Problemáticos'}
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)

if __name__ == "__main__":
    main()