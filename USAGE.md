# Guia de Uso - Feature Envy Detector

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
- **Limite mínimo de acessos**: Ajuste o slider para definir quantos acessos mínimos são necessários para considerar um bloco para análise
- **Valor padrão**: 4 acessos

### Resultados
O dashboard exibe:

#### Métricas Gerais
- **Telas Analisadas**: Número total de telas no projeto
- **Casos de Feature Envy**: Total de problemas encontrados
- **Telas com Problemas**: Quantas telas têm issues
- **Taxa de Problemas**: Percentual de telas com problemas

#### Visualizações
- **Gráfico de Pizza**: Distribuição de telas com/sem Feature Envy
- **Gráfico de Barras**: Casos de Feature Envy por tela
- **Gráficos de Acesso**: Para cada caso, mostra acessos locais vs externos

#### Detalhes por Tela
- **Expandir cada tela** para ver casos específicos
- **Gráficos de barras** mostrando distribuição de acessos
- **Lista de componentes invejados** com contagem de acessos

## 🔍 Interpretando os Resultados

### O que é Feature Envy?
Feature Envy ocorre quando um método acessa mais dados de outros objetos do que de seu próprio objeto.

### Sintomas Detectados:
- ✅ **Acessos Locais**: Interações com o próprio componente
- ❌ **Acessos Externos**: Interações com outros componentes
- ⚠️ **Problema**: Quando acessos externos > acessos locais

### Exemplo de Problema:
```javascript
// PROBLEMA: Este handler acessa mais outros componentes
Button1.Click {
    // 1 acesso local (Button1)
    // 5 acessos externos (TextBox1, Label1, etc.)
    TextBox1.Text = "Hello"
    Label1.Text = "World"
    // ... mais acessos externos
}
```

## 🛠️ Soluções Recomendadas

### 1. Refatoração de Métodos
- Mover lógica para componentes apropriados
- Criar métodos auxiliares nos componentes corretos

### 2. Reorganização de Responsabilidades
- Verificar se o handler está no componente correto
- Considerar mover funcionalidade para outros componentes

### 3. Padrões de Design
- Aplicar princípios SOLID
- Usar padrões como Observer ou Mediator

## 📁 Estrutura de Arquivos

```
featury_envy/
├── dashboard.py              # Interface principal
├── processador_feature_envy.py  # Lógica de análise
├── requirements.txt          # Dependências
├── README.md               # Documentação geral
├── USAGE.md               # Este guia
└── dataset/               # Arquivos de exemplo
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
