# Guia de Uso - Long Parameter List Detector

## 🚀 Como Executar

### 1. Ativar o Ambiente Virtual
```bash
# Windows
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

### 2. Executar o Dashboard
```bash
streamlit run dashboard.py
```

### 3. Acessar a Interface
- Abra o navegador no endereço: `http://localhost:8501`
- A interface será carregada automaticamente

## 📊 Funcionalidades do Dashboard

### Upload de Arquivo
1. Clique em "Browse files" ou arraste um arquivo .aia
2. Selecione o arquivo do seu projeto App Inventor
3. Clique em "🚀 Iniciar Análise"

### Configurações
- **Limite de parâmetros**: Ajuste o slider para definir quantos parâmetros são permitidos antes de ser considerado um code smell
- **Valor padrão**: 3 parâmetros

### Resultados
O dashboard exibe:

#### Métricas Gerais
- **Telas Analisadas**: Número total de telas no projeto
- **Procedimentos Encontrados**: Total de procedimentos detectados
- **Procedimentos com Muitos Parâmetros**: Procedimentos que excedem o limite
- **Taxa de Problemas**: Percentual de telas com problemas

#### Visualizações
- **Gráfico de Pizza**: Distribuição de telas com/sem problemas
- **Gráfico de Barras**: Procedimentos problemáticos por tela
- **Gráficos de Parâmetros**: Para cada procedimento problemático, mostra o número de parâmetros

#### Detalhes por Tela
- **Expandir cada tela** para ver procedimentos específicos
- **Gráficos de barras** mostrando número de parâmetros
- **Lista de parâmetros** com nomes detalhados

## 🔍 Interpretando os Resultados

### O que é Long Parameter List?
Long Parameter List ocorre quando um procedimento tem muitos parâmetros, dificultando sua compreensão e manutenção.

### Sintomas Detectados:
- ✅ **Procedimentos Normais**: Com 3 ou menos parâmetros
- ⚠️ **Procedimentos Problemáticos**: Com mais de 3 parâmetros
- 🚨 **Problema**: Quando parâmetros > limite configurado

### Exemplo de Problema:
```javascript
// PROBLEMA: Este procedimento tem muitos parâmetros
procedure CalcularTotal(
    valor1, valor2, valor3, valor4, valor5, valor6
) {
    // 6 parâmetros - muito difícil de manter
    return valor1 + valor2 + valor3 + valor4 + valor5 + valor6;
}
```

## 🛠️ Soluções Recomendadas

### 1. Agrupar Parâmetros
- Criar uma estrutura de dados (lista ou dicionário)
- Passar objetos em vez de parâmetros individuais

### 2. Dividir Procedimentos
- Quebrar em procedimentos menores
- Cada procedimento com responsabilidade específica

### 3. Padrões de Design
- Aplicar princípios SOLID
- Usar padrões como Builder ou Factory

## 📁 Estrutura de Arquivos

```
featury_envy/
├── dashboard.py                              # Interface principal
├── processador_correcto_parametros_longos_ou_feature_envy.py  # Lógica de análise
├── requirements.txt                          # Dependências
├── README.md                                # Documentação geral
├── USAGE.md                                 # Este guia
└── dataset/                                 # Arquivos de exemplo
    └── *.aia
```

## 🔧 Troubleshooting

### Problema: "Erro ao extrair arquivo .aia"
- Verifique se o arquivo não está corrompido
- Certifique-se de que é um arquivo .aia válido

### Problema: "Nenhum arquivo .bky encontrado"
- O projeto pode não ter telas configuradas
- Verifique se o arquivo .aia foi exportado corretamente

### Problema: Dashboard não carrega
- Verifique se o ambiente virtual está ativado
- Execute `pip install -r requirements.txt`
- Verifique se a porta 8501 está livre

## 📞 Suporte

Para dúvidas ou problemas:
- Abra uma issue no GitHub: https://github.com/gersongalante/featury_envy
- Entre em contato: gersongalante19@gmail.com
