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
    parse_blockly_xml_to_ast as parse_blockly_xml
)

# Funções de Feature Envy (adaptadas do arquivo correto)
def collect_component_accesses(block: Optional[Dict], access_list: List[str]):
    """
    Percorre recursivamente a AST de um bloco e coleta todos os acessos a componentes.
    """
    if not block:
        return

    block_type = block.get('type')

    # Verifica se o bloco é um acesso a um componente (método, getter ou setter)
    if block_type in ['component_method', 'component_set_get']:
        instance_name = block.get('mutation', {}).get('instance_name')
        if instance_name:
            access_list.append(instance_name)

    # Continua a recursão para todos os blocos filhos
    for value in block.get('values', []):
        collect_component_accesses(value.get('block'), access_list)
    for statement in block.get('statements', []):
        collect_component_accesses(statement.get('block'), access_list)

    collect_component_accesses(block.get('next'), access_list)

def find_feature_envy(structured_data: Dict, access_threshold: int) -> List[Dict]:
    """
    Analisa uma tela para encontrar manipuladores de eventos que exibem "Feature Envy".
    """
    envy_cases = []

    # Procura por blocos de manipulador de eventos
    event_handlers = [b for b in structured_data.get('blocks', []) if b.get('type') == 'component_event']

    for handler in event_handlers:
        handler_mutation = handler.get('mutation', {})
        host_component_name = handler_mutation.get('instance_name')
        event_name = handler_mutation.get('event_name')

        if not host_component_name:
            continue # Pula handlers malformados

        full_handler_name = f"{host_component_name}.{event_name}"

        # O corpo do handler está no primeiro statement
        body_start_block = None
        if handler.get('statements'):
            body_start_block = handler['statements'][0].get('block')

        if not body_start_block:
            continue # Handler sem corpo

        # Coleta todos os acessos a componentes dentro do corpo do handler
        accesses = []
        collect_component_accesses(body_start_block, accesses)

        # Calcula as métricas
        access_counts = Counter(accesses)
        total_accesses = len(accesses)

        # Se não houver acessos suficientes, não é relevante
        if total_accesses <= access_threshold:
            continue

        local_accesses = access_counts.get(host_component_name, 0)
        foreign_accesses = total_accesses - local_accesses

        # Aplica a heurística do Feature Envy
        if foreign_accesses > local_accesses:
            envy_details = {
                "handler_name": full_handler_name,
                "local_accesses": local_accesses,
                "foreign_accesses": foreign_accesses,
                "total_accesses": total_accesses,
                "envied_components": {comp: count for comp, count in access_counts.items() if comp != host_component_name}
            }
            envy_cases.append(envy_details)

    return envy_cases

# Configuração da página
st.set_page_config(
    page_title="Feature Envy Detector",
    page_icon="🔍",
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
    st.markdown('<h1 class="main-header">🔍 Feature Envy Detector</h1>', unsafe_allow_html=True)
    st.markdown("### Análise de Code Smells em Projetos App Inventor")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Parâmetros de análise
        st.subheader("Parâmetros de Análise")
        access_threshold = st.slider(
            "Limite mínimo de acessos",
            min_value=1,
            max_value=10,
            value=4,
            help="Número mínimo de acessos para considerar um bloco para análise"
        )
        
        st.markdown("---")
        st.markdown("### 📊 Sobre Feature Envy")
        st.info("""
        **Feature Envy** é um code smell que ocorre quando um método acessa mais dados 
        de outros objetos do que de seu próprio objeto.
        
        **Sintomas:**
        - Método que chama muitos métodos de outro objeto
        - Método que acessa muitos campos de outro objeto
        - Método que parece "pertencer" a outra classe
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
                    results = analyze_project(uploaded_file, access_threshold)
                    display_results(results)
    
    with col2:
        st.header("📈 Estatísticas")
        
        if 'analysis_results' in st.session_state:
            results = st.session_state.analysis_results
            display_statistics(results)
        else:
            st.info("Faça upload de um arquivo .aia para ver as estatísticas")

def analyze_project(uploaded_file, access_threshold):
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
                    envy_cases = find_feature_envy(structured_data, access_threshold)
                    
                    screen_result = {
                        'screen_name': screen_name,
                        'envy_cases': envy_cases,
                        'total_handlers': len([b for b in structured_data.get('blocks', []) 
                                             if b.get('type') == 'component_event']),
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
    total_envy_cases = sum(len(screen['envy_cases']) for screen in results)
    screens_with_envy = len([screen for screen in results if screen['envy_cases']])
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Telas Analisadas", total_screens)
    
    with col2:
        st.metric("Casos de Feature Envy", total_envy_cases)
    
    with col3:
        st.metric("Telas com Problemas", screens_with_envy)
    
    with col4:
        if total_screens > 0:
            percentage = (screens_with_envy / total_screens) * 100
            st.metric("Taxa de Problemas", f"{percentage:.1f}%")
        else:
            st.metric("Taxa de Problemas", "0%")
    
    # Resultados detalhados por tela
    st.header("📋 Resultados Detalhados")
    
    for screen_result in results:
        with st.expander(f"📱 {screen_result['screen_name']}", expanded=True):
            envy_cases = screen_result['envy_cases']
            
            if not envy_cases:
                st.success("✅ Nenhum caso de Feature Envy detectado nesta tela")
            else:
                st.warning(f"⚠️ {len(envy_cases)} caso(s) de Feature Envy encontrado(s)")
                
                for i, case in enumerate(envy_cases, 1):
                    st.markdown(f"**Caso #{i}:** {case['handler_name']}")
                    
                    # Gráfico de acessos
                    fig = go.Figure(data=[
                        go.Bar(
                            x=['Acessos Locais', 'Acessos Externos'],
                            y=[case['local_accesses'], case['foreign_accesses']],
                            marker_color=['#2ecc71', '#e74c3c']
                        )
                    ])
                    
                    fig.update_layout(
                        title=f"Distribuição de Acessos - {case['handler_name']}",
                        xaxis_title="Tipo de Acesso",
                        yaxis_title="Número de Acessos",
                        height=300
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Detalhes dos componentes invejados
                    if case['envied_components']:
                        st.markdown("**Componentes Invejados:**")
                        for component, count in case['envied_components'].items():
                            st.markdown(f"- {component}: {count} acessos")
                    
                    st.markdown("---")

def display_statistics(results):
    """Exibe estatísticas gerais"""
    
    if not results:
        return
    
    # Calcular estatísticas
    total_envy_cases = sum(len(screen['envy_cases']) for screen in results)
    screens_with_envy = len([screen for screen in results if screen['envy_cases']])
    total_screens = len(results)
    
    # Gráfico de pizza - Telas com/sem problemas
    fig_pie = px.pie(
        values=[screens_with_envy, total_screens - screens_with_envy],
        names=['Com Feature Envy', 'Sem Feature Envy'],
        title="Distribuição de Telas",
        color_discrete_sequence=['#e74c3c', '#2ecc71']
    )
    
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Gráfico de barras - Casos por tela
    screen_names = [screen['screen_name'] for screen in results]
    envy_counts = [len(screen['envy_cases']) for screen in results]
    
    fig_bar = px.bar(
        x=screen_names,
        y=envy_counts,
        title="Casos de Feature Envy por Tela",
        labels={'x': 'Tela', 'y': 'Casos de Feature Envy'}
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)

if __name__ == "__main__":
    main()