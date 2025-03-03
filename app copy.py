import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from deep_translator import GoogleTranslator
import io
import re
from pdf2image import convert_from_bytes
import pytesseract

# Use a biblioteca ReportLab ao invés da FPDF para melhor suporte a Unicode
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_JUSTIFY

# Título da aplicação
st.title("Tradução de Livro em PDF para Português do Brasil")

# Upload do arquivo PDF
uploaded_file = st.file_uploader("Faça upload do arquivo PDF (livro em inglês)", type=["pdf"])

if uploaded_file is not None:
    st.write("Arquivo carregado com sucesso!")

    # Salvar bytes do arquivo para reutilização
    pdf_bytes = uploaded_file.read()
    
    # Extração do texto do PDF
    pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
    full_text = ""

    for page_num, page in enumerate(pdf_reader.pages):
        text = page.extract_text()
        if text:
            full_text += text.strip() + "\n"
        else:
            st.warning(f"Página {page_num + 1} pode estar vazia ou ser uma imagem. Tentando OCR...")

            # Converter página para imagem e aplicar OCR
            images = convert_from_bytes(pdf_bytes, first_page=page_num + 1, last_page=page_num + 1)
            for img in images:
                ocr_text = pytesseract.image_to_string(img, lang="eng", config="--psm 3")
                full_text += ocr_text.strip() + "\n"

    if not full_text.strip():
        st.error("Erro: O PDF não contém texto extraível nem via OCR.")
        st.stop()

    st.write("Extração de texto concluída!")

    # Exibir um trecho do texto extraído
    st.text_area("Texto extraído (pré-tradução)", full_text[:1000])

    # Dividir o texto em partes menores para tradução
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=4500, chunk_overlap=200)
    chunks = text_splitter.split_text(full_text)
    st.write(f"Total de {len(chunks)} partes para tradução.")

    # Inicializa o tradutor
    translator = GoogleTranslator(source="en", target="pt")

    translated_chunks = []
    progress_bar = st.progress(0)

    for i, chunk in enumerate(chunks):
        try:
            translated_text = translator.translate(chunk)
            # Mantenha acentos e caracteres especiais do português (apenas remova caracteres verdadeiramente problemáticos)
            translated_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', translated_text)
            translated_chunks.append(translated_text)
        except Exception as e:
            st.error(f"Erro ao traduzir parte {i + 1}: {e}")
            break
        progress_bar.progress((i + 1) / len(chunks))

    translated_text = "\n".join(translated_chunks)
    st.write("Tradução concluída!")

    # Exibir um trecho do texto traduzido para verificação
    st.text_area("Texto traduzido", translated_text[:1000])

    # Gerar PDF com a tradução usando ReportLab (mais robusta com Unicode)
    try:
        # Buffer para armazenar PDF
        buffer = io.BytesIO()
        
        # Configurar o documento PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )
        
        # Lista para armazenar elementos do PDF
        elements = []
        
        # Configurar estilos
        styles = getSampleStyleSheet()
        
        # Criar estilo personalizado para o texto principal
        normal_style = ParagraphStyle(
            'NormalWithSpacing',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,  # Espaçamento entre linhas
            alignment=TA_JUSTIFY
        )
        
        # Processar o texto traduzido
        paragraphs = translated_text.split('\n\n')
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            # Limpar caracteres de controle problemáticos, mantendo acentos e caracteres especiais
            clean_paragraph = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', paragraph)
            
            # Adicionar parágrafo com tratamento de erros
            try:
                p = Paragraph(clean_paragraph, normal_style)
                elements.append(p)
                elements.append(Spacer(1, 6))  # Espaço entre parágrafos
            except Exception as e:
                st.warning(f"Erro ao processar um parágrafo: {e}")
                # Tenta dividir o parágrafo problemático em frases
                sentences = re.split(r'[.!?]+', clean_paragraph)
                for sentence in sentences:
                    if not sentence.strip():
                        continue
                    try:
                        p = Paragraph(sentence.strip() + ".", normal_style)
                        elements.append(p)
                    except:
                        st.warning(f"Ignorando uma frase problemática.")
                elements.append(Spacer(1, 6))
        
        # Construir o PDF
        doc.build(elements)
        
        # Obter o PDF do buffer
        pdf_data = buffer.getvalue()
        buffer.close()
        
        # Oferecer download do PDF gerado
        st.download_button(
            label="Baixar PDF Traduzido",
            data=pdf_data,
            file_name="livro_traduzido.pdf",
            mime="application/pdf"
        )
        st.success("PDF gerado com sucesso! Clique no botão acima para fazer o download.")
        
    except Exception as e:
        st.error(f"Erro ao gerar o PDF: {e}")
        
        # Oferecer o texto como alternativa
        st.write("Não foi possível gerar o PDF, mas você pode baixar o texto traduzido:")
        st.download_button(
            label="Baixar Texto Traduzido (.txt)",
            data=translated_text,
            file_name="traducao.txt",
            mime="text/plain"
        )