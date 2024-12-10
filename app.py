import streamlit as st
import os
import openai
from fpdf import FPDF
from io import BytesIO
from gtts import gTTS

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
        .main-container {
            text-align: center;
            margin-top: 50px;
        }
        .title {
            font-size: 40px;
            font-weight: bold;
            color: #3f83f8;
            text-align: center;
            margin-bottom: 20px;
        }
        .subtitle {
            font-size: 20px;
            color: #9ba1ab;
            margin-top: -10px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Título
st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown('<div class="title">Storyme.life</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Step 1: Begin your story</div>', unsafe_allow_html=True)

# Passo 1: Gravação do áudio inicial
if st.session_state.audio1_text is None:
    st.markdown('<div class="microphone-icon">🎤</div>', unsafe_allow_html=True)
    audio1 = st.audio_input("🎙️ Click below to record your story:")
    if audio1 is not None:
        st.write("Processing your audio...")
        audio_file = BytesIO(audio1.read())
        try:
            audio_file.name = "audio1.wav"
            response = openai.Audio.transcribe("whisper-1", audio_file)
            st.session_state.audio1_text = response.get("text", "Transcription failed.")
            st.success("Audio processed successfully!")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Passo 2: Exibindo perguntas
if st.session_state.audio1_text:
    st.markdown('<div class="questions-container">', unsafe_allow_html=True)
    st.write("### Questions based on your story:")
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
    st.markdown('</div>', unsafe_allow_html=True)

# Passo 3: Gravação do segundo áudio para responder perguntas
if st.session_state.questions:
    st.subheader("Step 2: Record your answers")
    audio2 = st.audio_input("🎙️ Record your answers below:")
    if audio2 is not None and st.session_state.audio2_text is None:
        st.write("Processing your audio answers...")
        audio_file = BytesIO(audio2.read())
        try:
            audio_file.name = "audio2.wav"
            response = openai.Audio.transcribe("whisper-1", audio_file)
            st.session_state.audio2_text = response.get("text", "Transcription failed.")
            st.success("Answers processed successfully!")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Passo 4: Gerar a história final
if st.session_state.audio1_text and st.session_state.audio2_text:
    st.subheader("Generate your final story")
    if st.button("Generate Story"):
        try:
            prompt = (
                f"Você é um grande escritor e contador de história. Crie um título e subtítulos para cada capítulo "
                f"baseado na história abaixo:\n\n"
                f"Informações iniciais: {st.session_state.audio1_text}\n"
                f"Respostas às perguntas: {st.session_state.audio2_text}"
            )
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": prompt}]
            )
            story_content = response["choices"][0]["message"]["content"].split("\n")
            st.session_state.final_story = "\n".join(story_content[1:])
            st.session_state.story_title = story_content[0]
            st.success("Story generated successfully!")
            st.markdown(f"### {st.session_state.story_title}")
            st.write(st.session_state.final_story)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Passo 5: Geração do eBook
# Geração do eBook
if st.session_state.final_story:
    st.subheader("Download your eBook as PDF")
    if st.button("Download eBook"):
        try:
            # Caminho para as fontes Unicode
            font_dir = "fonts/"
            font_regular = os.path.join(font_dir, "FreeSerif-Regular.ttf")
            font_bold = os.path.join(font_dir, "FreeSerif-Bold.ttf")

            # Criar o PDF
            pdf = FPDF()
            pdf.add_page()

            # Adicionar as fontes
            pdf.add_font("FreeSerif", "", font_regular, uni=True)  # Regular
            pdf.add_font("FreeSerif", "B", font_bold, uni=True)  # Negrito

            # Configurar a capa
            pdf.set_font("FreeSerif", "B", size=24)
            pdf.cell(0, 10, st.session_state.story_title, ln=True, align="C")
            pdf.ln(20)

            # Páginas Internas
            pdf.add_page()
            pdf.set_font("FreeSerif", size=12)
            pdf.multi_cell(0, 10, st.session_state.final_story)

            # Salvar no buffer
            pdf_output = BytesIO()
            pdf.output(pdf_output)
            pdf_output.seek(0)

            # Botão de download
            st.download_button(
                label="Download PDF",
                data=pdf_output,
                file_name="ebook.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")


    # Geração do Audiobook
    st.subheader("Generate and download your audiobook")
    st.radio("Choose the narration voice:", ["Feminina", "Masculina"], key="narration_voice")
    if st.button("Generate Audiobook"):
        try:
            if st.session_state.narration_voice == "Feminina":
                tts = gTTS(st.session_state.final_story, lang="pt")
            else:
                tts = gTTS(st.session_state.final_story, lang="pt", slow=True)

            # Salvar no buffer
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            st.audio(audio_buffer, format="audio/mp3")
            st.success("Audiobook generated successfully!")
            st.download_button(
                label="Download Audiobook",
                data=audio_buffer,
                file_name="audiobook.mp3",
                mime="audio/mp3"
            )
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
