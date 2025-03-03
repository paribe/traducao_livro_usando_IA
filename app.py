import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from deep_translator import GoogleTranslator
import io
import re
from pdf2image import convert_from_bytes
import pytesseract
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
import time

def extract_text_from_pdf(pdf_bytes):
    pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
    full_text = ""
    
    for page_num, page in enumerate(pdf_reader.pages):
        text = page.extract_text()
        if text:
            full_text += text.strip() + "\n"
        else:
            st.warning(f"Página {page_num + 1} pode estar vazia ou ser uma imagem. Tentando OCR...")
            images = convert_from_bytes(pdf_bytes, first_page=page_num + 1, last_page=page_num + 1)
            for img in images:
                ocr_text = pytesseract.image_to_string(img, lang="eng", config="--psm 3")
                full_text += ocr_text.strip() + "\n"
    
    if not full_text.strip():
        st.error("Erro: O PDF não contém texto extraível nem via OCR.")
        return None
    
    return full_text

def translate_text(text, source_lang="en", target_lang="pt", chunk_size=4500, chunk_overlap=200, max_retries=3, delay=1):
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_text(text)
    translator = GoogleTranslator(source=source_lang, target=target_lang)
    translated_chunks = []
    progress_bar = st.progress(0)
    
    for i, chunk in enumerate(chunks):
        for attempt in range(max_retries):
            try:
                translated_text = translator.translate(chunk)
                translated_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', translated_text)
                translated_chunks.append(translated_text)
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    st.warning(f"Erro ao traduzir (tentativa {attempt + 1}): {e}. Retentando em {delay} segundos.")
                    time.sleep(delay)
                    delay *= 2
                else:
                    st.error(f"Erro ao traduzir parte {i + 1}: {e}. Número máximo de tentativas excedido.")
                    return None
        progress_bar.progress((i + 1) / len(chunks))
    
    return "\n".join(translated_chunks)

def create_translated_pdf(translated_text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle('NormalWithSpacing', parent=styles['Normal'], fontSize=10, leading=14, alignment=TA_JUSTIFY)
    
    paragraphs = translated_text.split('\n\n')
    for paragraph in paragraphs:
        if not paragraph.strip():
            continue
        clean_paragraph = re.sub(r'[^\x20-\x7E]', '', paragraph)
        try:
            p = Paragraph(clean_paragraph, normal_style)
            elements.append(p)
            elements.append(Spacer(1, 6))
        except Exception as e:
            st.warning(f"Erro ao processar um parágrafo: {e}")
            sentences = re.split(r'[.!?]+', clean_paragraph)
            for sentence in sentences:
                if not sentence.strip():
                    continue
                try:
                    p = Paragraph(sentence.strip() + ".", normal_style)
                    elements.append(p)
                except:
                    st.warning("Ignorando uma frase problemática.")
            elements.append(Spacer(1, 6))
    
    doc.build(elements)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data

# Streamlit App
st.title("Tradução de Livro em PDF para Português do Brasil")
uploaded_file = st.file_uploader("Faça upload do arquivo PDF (livro em inglês)", type=["pdf"])

if uploaded_file is not None:
    st.write("Arquivo carregado com sucesso!")
    pdf_bytes = uploaded_file.read()
    
    st.write("Extraindo texto do PDF...")
    full_text = extract_text_from_pdf(pdf_bytes)
    if full_text is None:
        st.stop()
    
    st.text_area("Texto extraído (pré-tradução)", full_text[:2000])
    
    st.write("Traduzindo texto...")
    translated_text = translate_text(full_text)
    if translated_text is None:
        st.error("Erro: Falha na tradução. Tente novamente mais tarde.")
        st.stop()
    
    st.text_area("Texto traduzido", translated_text[:2000])
    
    st.write("Gerando PDF...")
    try:
        pdf_data = create_translated_pdf(translated_text)
        output_filename = st.text_input("Nome do arquivo PDF de saída:", "livro_traduzido.pdf")
        
        with open("debug_traduzido.pdf", "wb") as f:
            f.write(pdf_data)  # Salva localmente para debug
        
        st.download_button(label="Baixar PDF Traduzido", data=pdf_data, file_name=output_filename, mime="application/pdf")
        st.success("PDF gerado com sucesso! Clique no botão acima para fazer o download.")
    except Exception as e:
        st.error(f"Erro ao gerar o PDF: {e}")
        st.write("Não foi possível gerar o PDF, mas você pode baixar o texto traduzido:")
        st.download_button(label="Baixar Texto Traduzido (.txt)", data=translated_text, file_name="traducao.txt", mime="text/plain")