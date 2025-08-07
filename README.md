# Feature Envy Detector

Um dashboard interativo para análise de code smells "Feature Envy" em projetos App Inventor (.aia).

## Descrição

Este projeto implementa um detector de Feature Envy para aplicações desenvolvidas no MIT App Inventor. O Feature Envy é um code smell que ocorre quando um método acessa mais dados de outros objetos do que de seu próprio objeto.

## Funcionalidades

- **Upload de arquivos .aia**: Interface para carregar projetos App Inventor
- **Análise automática**: Detecção de Feature Envy em manipuladores de eventos
- **Dashboard interativo**: Visualização de resultados com gráficos e métricas
- **Relatórios detalhados**: Análise completa com recomendações

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/gersongalante/featury_envy.git
cd featury_envy
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
```

3. Ative o ambiente virtual:
```bash
# Windows
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

1. Execute o dashboard:
```bash
streamlit run dashboard.py
```

2. Abra o navegador no endereço indicado (geralmente http://localhost:8501)

3. Faça upload de um arquivo .aia e visualize os resultados

## Estrutura do Projeto

```
featury_envy/
├── dashboard.py              # Interface Streamlit
├── processador_feature_envy.py  # Lógica de análise
├── requirements.txt          # Dependências
├── README.md               # Documentação
└── dataset/               # Arquivos de exemplo
    └── *.aia
```

## Tecnologias Utilizadas

- **Streamlit**: Interface web interativa
- **Pandas**: Manipulação de dados
- **Plotly**: Visualizações gráficas
- **XML ElementTree**: Parsing de arquivos .aia

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## Autor

Gerson Galante - [GitHub](https://github.com/gersongalante)
