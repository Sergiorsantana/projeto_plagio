import fitz  # PyMuPDF para leitura de PDFs
import docx  # Para leitura de arquivos .docx
import difflib  # Para comparação de textos
import openai  # Para detecção de IA
import os

# Configuração da chave da API OpenAI (substitua pela sua chave válida)
openai.api_key = "SUA_CHAVE_AQUI"

# Função para extrair texto de um arquivo PDF
def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        return text
    except Exception as e:
        print(f"Erro ao processar PDF {pdf_path}: {e}")
        return ""

# Função para extrair texto de um arquivo DOCX
def extract_text_from_docx(docx_path):
    try:
        doc = docx.Document(docx_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Erro ao processar DOCX {docx_path}: {e}")
        return ""

# Função para verificar similaridade entre textos (detecção de plágio)
def check_similarity(text1, text2):
    similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
    return similarity

# Função para detectar se um texto foi gerado por IA
def detect_ai_generated_text(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "Esse texto foi gerado por IA ou humano? Responda apenas com 'IA' ou 'Humano'."},
                      {"role": "user", "content": text[:1000]}],  # Envia apenas os primeiros 1000 caracteres
            max_tokens=5
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print(f"Erro ao consultar OpenAI: {e}")
        return "Erro"

# Função principal para processar os documentos
def analyze_documents(directory="documentos"):
    reference_text = "Texto acadêmico original usado como referência para detecção de plágio."
    
    results = []
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        ext = os.path.splitext(filename)[1].lower()

        if ext == ".pdf":
            text = extract_text_from_pdf(file_path)
        elif ext == ".docx":
            text = extract_text_from_docx(file_path)
        else:
            continue  # Ignora arquivos que não sejam PDF ou DOCX

        # Verificar similaridade com texto de referência
        similarity = check_similarity(text, reference_text)
        plagiarism_flag = "Plágio detectado" if similarity > 0.7 else "Sem plágio significativo"

        # Verificar se o texto foi gerado por IA
        ai_detected = detect_ai_generated_text(text)

        # Adicionar ao relatório
        results.append({
            "arquivo": filename,
            "similaridade": similarity,
            "plágio": plagiarism_flag,
            "origem": "Possível IA" if ai_detected == "IA" else "Humano"
        })

    return results

# Rodar análise e exibir relatório
if __name__ == "__main__":
    resultados = analyze_documents()
    print("\nRelatório de Análise:")
    for resultado in resultados:
        print(f"Arquivo: {resultado['arquivo']}")
        print(f" - Similaridade: {resultado['similaridade']:.2%}")
        print(f" - Status: {resultado['plágio']}")
        print(f" - Origem: {resultado['origem']}")
        print("-" * 40)
