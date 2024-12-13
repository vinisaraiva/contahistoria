import streamlit as st
import os
from openai import Client
from fpdf import FPDF
from io import BytesIO
from gtts import gTTS

# Configuração da API OpenAI
openai_client = Client(api_key=os.environ.get("OPENAI_API_KEY"))

# Configuração inicial do Streamlit
st.set_page_config(page_title="Storyme.life", layout="centered", initial_sidebar_state="collapsed")

# Inicializando estados da aplicação
if "audio1_text" not in st.session_state:
    st.session_state.audio1_text = None
if "questions" not in st.session_state:
    st.session_state.questions = None
if "audio2_text" not in st.session_state:
    st.session_state.audio2_text = None
if "final_story" not in st.session_state:
    st.session_state.final_story = None
if "narration_voice" not in st.session_state:
    st.session_state.narration_voice = "Feminina"
if "story_title" not in st.session_state:
    st.session_state.story_title = None
if "ebook_pdf" not in st.session_state:
    st.session_state.ebook_pdf = None
if "audiobook_mp3" not in st.session_state:
    st.session_state.audiobook_mp3 = None

# Estilo CSS
st.markdown("""
    <style>
        body {
            background-color: #0e1117;
            color: #ffffff;
            font-family: Arial, sans-serif;
        }
    </style>
""", unsafe_allow_html=True)

# Função para fazer upload e transcrever áudio com a API OpenAI
def transcrever_audio(audio_bytes, file_name="audio.wav"):
    try:
        # Salvar o áudio em um arquivo temporário para upload
        with open(file_name, "wb") as temp_audio_file:
            temp_audio_file.write(audio_bytes)

        # Enviar o arquivo para transcrição
        with open(file_name, "rb") as audio_file:
            response = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return response.text
    except Exception as e:
        return f"Error during transcription: {e}"

# Função para criar o eBook com uma linha decorativa
def criar_ebook_pdf(title, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(0, 10, title, ln=True, align="C")
    
    # Adicionar linha decorativa
    pdf.set_draw_color(0, 0, 255)  # Azul
    pdf.set_line_width(1)
    pdf.line(10, 20, 200, 20)  # Linha horizontal

    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.multi_cell(0, 10, content)
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# Passo 1: Gravação do primeiro áudio
if st.session_state.audio1_text is None:
    st.markdown("### Step 1: Record your story")
    audio_file = st.audio_input("🎙️ Record your story below:")
    if audio_file:
        st.audio(audio_file, format="audio/wav")
        try:
            st.session_state.audio1_text = transcrever_audio(audio_file.read(), file_name="story_audio.wav")
            st.success("Audio processed successfully!")
            st.write(f"Transcription: {st.session_state.audio1_text}")
        except Exception as e:
            st.error(f"An error occurred during transcription: {str(e)}")

# Passo 2: Exibindo perguntas
if st.session_state.audio1_text:
    st.markdown("### Questions based on your story:")
    if st.session_state.questions is None:
        try:
            prompt = f"Analyze the following story: {st.session_state.audio1_text}. Generate 5 clarifying questions to complete the story."
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": prompt}]
            )
            st.session_state.questions = response.choices[0].message.content
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    if st.session_state.questions:
        st.write(st.session_state.questions)

# Passo 3: Gravação do segundo áudio
if st.session_state.questions and st.session_state.audio2_text is None:
    st.markdown("### Step 2: Record your answers")
    audio_file = st.audio_input("🎙️ Record your answers below:")
    if audio_file:
        st.audio(audio_file, format="audio/wav")
        try:
            st.session_state.audio2_text = transcrever_audio(audio_file.read(), file_name="answers_audio.wav")
            st.success("Answers processed successfully!")
            st.write(f"Transcription: {st.session_state.audio2_text}")
        except Exception as e:
            st.error(f"An error occurred during transcription: {str(e)}")

# Passo 4: Gerar história, eBook e audiobook
if st.session_state.audio1_text and st.session_state.audio2_text:
    st.subheader("Generate your story, eBook, and audiobook")
    tone = st.selectbox("Choose the tone of the narration:", ["Neutral", "Dramatic", "Animated", "Suspense"])
    voice = st.radio("Choose the narration voice:", ["Feminina", "Masculina"])

    if st.button("Generate Story, eBook, and Audiobook"):
        try:
            # Prompt para gerar história
            prompt = (
                f"Você é um escritor talentoso, premiado, com mais de 20 livros publicados e doutorado em letras. Crie uma história com o tom {tone.lower()} baseada"
                f"nas informações abaixo. A história deve incluir um título geral, capítulos com títulos e um texto. O texto não precisa sinalizar com o nome Texto no seu inicio"
                f"A história deve ser coesa com inicio meio e fim. Deve variar o tamanho dos capitulos, uns com 500 palavras, uns com 700 e uns com 600 palavras.\n\n"
                f"Informações iniciais: {st.session_state.audio1_text}\n"
                f"Respostas às perguntas: {st.session_state.audio2_text}"
            )

            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": prompt}]
            )
            story_content = response.choices[0].message.content
            st.session_state.story_title = story_content.split("\n")[0]
            st.session_state.final_story = "\n".join(story_content.split("\n")[1:])

            # Gerar eBook
            st.session_state.ebook_pdf = criar_ebook_pdf(st.session_state.story_title, st.session_state.final_story)

            # Gerar Audiobook
            tts = gTTS(text=st.session_state.final_story, lang="pt")
            audio_output = BytesIO()
            tts.write_to_fp(audio_output)
            audio_output.seek(0)
            st.session_state.audiobook_mp3 = audio_output

            st.success("Story, eBook, and Audiobook generated successfully!")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Oferecer download do eBook e Audiobook
if st.session_state.ebook_pdf:
    st.download_button(
        label="Download eBook (PDF)",
        data=st.session_state.ebook_pdf,
        file_name="ebook.pdf",
        mime="application/pdf"
    )

if st.session_state.audiobook_mp3:
    st.download_button(
        label="Download Audiobook (MP3)",
        data=st.session_state.audiobook_mp3,
        file_name="audiobook.mp3",
        mime="audio/mp3"
    )
