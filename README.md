# 📖 Tradução de Livro em PDF para Português do Brasil

Este projeto permite a tradução automática de arquivos PDF escritos em inglês para português do Brasil. Ele utiliza a biblioteca `Streamlit` para criar uma interface amigável e `deep_translator` para realizar a tradução. O resultado é gerado como um novo arquivo PDF traduzido, pronto para download.

## 🚀 Funcionalidades
- 📂 **Upload de arquivos PDF** (somente em inglês)
- 🔍 **Extração do texto** do PDF
- 🌍 **Tradução automática** do texto
- 📄 **Geração de um novo PDF** traduzido
- 📥 **Download do PDF traduzido**

## 🛠️ Tecnologias Utilizadas
- [Python 3.12](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [PyPDF2](https://pypdf2.readthedocs.io/)
- [deep_translator](https://pypi.org/project/deep-translator/)
- [FPDF](https://pyfpdf.readthedocs.io/)
- [LangChain](https://python.langchain.com/) (para dividir o texto em partes menores)

## 🏗️ Instalação e Configuração
1. Clone este repositório:
   ```sh
   git clone https://github.com/paribe/traducao-livro_usando_ia.git
   cd traducao-livros
   ```
2. Crie e ative um ambiente virtual (opcional, mas recomendado):
   ```sh
   python -m venv venv
   source venv/bin/activate  # No Windows use: venv\Scripts\activate
   ```
3. Instale as dependências usando Poetry:
   ```sh
   poetry install
   ```
   Caso esteja usando `pip`:
   ```sh
   pip install -r requirements.txt
   ```

## ▶️ Como Executar
Para iniciar o aplicativo Streamlit, execute:
```sh
streamlit run app.py
```
Isso abrirá a interface web no navegador para upload e tradução de arquivos PDF.

## 📌 Estrutura do Projeto
```
/
├── app.py               # Arquivo principal do projeto
├── requirements.txt     # Lista de dependências para instalação via pip
├── README.md            # Documentação do projeto
├── venv/                # Ambiente virtual (opcional)
└── data/                # Pasta para armazenar PDFs processados
```

## 📝 Licença
Este projeto está licenciado sob a [MIT License](https://opensource.org/licenses/MIT). Sinta-se à vontade para usá-lo e contribuir!

## 🤝 Contribuição
Se desejar contribuir, siga estas etapas:
1. Faça um **fork** do repositório
2. Crie um novo **branch** para sua funcionalidade (`git checkout -b minha-feature`)
3. Faça as alterações e **commite** (`git commit -m 'Minha nova feature'`)
4. Faça um **push** para o branch (`git push origin minha-feature`)
5. Abra um **Pull Request**
