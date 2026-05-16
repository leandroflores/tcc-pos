# Análise dos Determinantes Socioeconômicos do Desempenho Educacional no Brasil

Este projeto reúne scripts em Python desenvolvidos para apoiar o Trabalho de Conclusão de Curso do MBA em Data Science e Analytics.

O objetivo do estudo é investigar a relação entre o desempenho dos estudantes do ensino médio nas avaliações do Sistema de Avaliação da Educação Básica (SAEB) e fatores socioeconômicos, demográficos e estruturais dos municípios brasileiros.

A análise utiliza dados públicos de fontes oficiais, como o Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira (INEP), o Sistema de Avaliação da Educação Básica (SAEB), o Censo Escolar e indicadores socioeconômicos do Instituto Brasileiro de Geografia e Estatística (IBGE).

## Objetivo

Construir uma base de dados integrada para analisar a associação entre indicadores municipais e o desempenho educacional em Língua Portuguesa e Matemática no ensino médio.

## Fontes de Dados

As principais fontes de dados utilizadas no projeto são:

- SAEB;
- Microdados do SAEB;
- Censo Escolar;
- Indicadores socioeconômicos do IBGE;
- Outras bases públicas complementares, quando necessário.

## Etapas do Projeto

O projeto está organizado nas seguintes etapas:

1. Coleta dos dados públicos;
2. Limpeza e padronização das bases;
3. Integração dos dados por município;
4. Análise exploratória dos dados;
5. Construção de indicadores educacionais e socioeconômicos;
6. Aplicação de técnicas estatísticas;
7. Aplicação de modelos de aprendizado de máquina;
8. Avaliação dos resultados;
9. Geração de tabelas, gráficos e arquivos finais para o TCC.

## Tecnologias Utilizadas

- Python;
- Pandas;
- NumPy;
- Scikit-learn;
- Matplotlib;
- Seaborn;
- Jupyter Notebook;
- Requests;
- Git e GitHub.

## Estrutura do Projeto

```text
tcc-pos/
├── data/
│   ├── raw/
│   ├── processed/
│   └── final/
├── notebooks/
├── src/
│   ├── coleta/
│   ├── tratamento/
│   ├── analise/
│   └── modelos/
├── outputs/
│   ├── graficos/
│   ├── tabelas/
│   └── relatorios/
├── requirements.txt
├── README.md
└── .gitignore
```
