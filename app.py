import streamlit as st
import os
import openai
from fpdf import FPDF
from io import BytesIO
from gtts import gTTS
from fpdf.enums import XPos, YPos
import textwrap

# Configuração da API OpenAI
openai.api_key = os.environ.get("openai_apikey")

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

# Função para transcrever áudio usando a API OpenAI
def transcrever_audio(audio_file):
    try:
        response = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file
        )
        return response["text"]
    except Exception as e:
        return f"Error during transcription: {e}"

# Passo 1: Gravação do primeiro áudio
if st.session_state.audio1_text is None:
    st.markdown("### Step 1: Record your story")
    audio_file = st.audio_input("🎙️ Record your story below:")
    if audio_file:
        try:
            st.audio(audio_file, format="audio/wav")
            st.session_state.audio1_text = transcrever_audio(audio_file)
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
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": prompt}]
            )
            st.session_state.questions = response["choices"][0]["message"]["content"]
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    if st.session_state.questions:
        st.write(st.session_state.questions)

# Passo 3: Gravação do segundo áudio
if st.session_state.questions and st.session_state.audio2_text is None:
    st.markdown("### Step 2: Record your answers")
    audio_file = st.audio_input("🎙️ Record your answers below:")
    if audio_file:
        try:
            st.audio(audio_file, format="audio/wav")
            st.session_state.audio2_text = transcrever_audio(audio_file)
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
                f"Você é um escritor talentoso. Crie uma história com o tom {tone.lower()} baseada "
                f"nas informações abaixo. A história deve incluir um título geral, capítulos com títulos e "
                f"um texto coeso. Cada capítulo deve ter pelo menos 500 palavras.\n\n"
                f"Informações iniciais: {st.session_state.audio1_text}\n"
                f"Respostas às perguntas: {st.session_state.audio2_text}"
            )
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": prompt}]
            )
            story_content = response["choices"][0]["message"]["content"]
            st.session_state.story_title = story_content.split("\n")[0]
            st.session_state.final_story = "\n".join(story_content.split("\n")[1:])

            # Gerar eBook
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, story_content)
            pdf_output = BytesIO()
            pdf.output(pdf_output)
            pdf_output.seek(0)
            st.download_button("Download eBook (PDF)", data=pdf_output, file_name="ebook.pdf", mime="application/pdf")

            # Gerar Audiobook
            tts = gTTS(text=st.session_state.final_story, lang="pt")
            audio_output = BytesIO()
            tts.write_to_fp(audio_output)
            audio_output.seek(0)
            st.audio(audio_output, format="audio/mp3")
            st.download_button("Download Audiobook (MP3)", data=audio_output, file_name="audiobook.mp3", mime="audio/mp3")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
