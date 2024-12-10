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
            color: #blue;
            text-align: center;
            margin-bottom: 20px;

        }
        .subtitle {
            font-size: 20px;
            color: #9ba1ab;
            margin-top: -10px;
            text-align: center;
        }
        .button-container {
            margin-top: 30px;
        }
        .record-button, .response-button {
            background-color: #1f2937;
            color: #ffffff;
            font-size: 18px;
            font-weight: bold;
            padding: 10px 20px;
            border: 2px solid #3f83f8;
            border-radius: 5px;
            cursor: pointer;
        }
        .record-button:hover, .response-button:hover {
            background-color: #3f83f8;
        }
        .microphone-icon {
            font-size: 60px;
            color: #3f83f8;
            margin-top: 20px;
            text-align: center;
        }
        .questions-container {
            background-color: #1f2937;
            padding: 15px;
            border-radius: 5px;
            color: #ffffff;
            text-align: left;
            margin-top: 20px;
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

# Passo 4: Gerar a história, eBook e audiobook com opções de tom e voz
if st.session_state.audio1_text and st.session_state.audio2_text:
    st.subheader("Generate your story, eBook, and audiobook")
    
    # Escolha do tom da narração
    tone = st.selectbox(
        "Choose the tone of the narration:",
        ["Neutral", "Dramatic", "Animated", "Suspense"],
        key="narration_tone"
    )
    
    # Escolha da voz
    voice = st.radio(
        "Choose the narration voice:",
        ["Feminina", "Masculina"],
        key="narration_voice"
    )

    # Botão único para gerar história, eBook e audiobook
    if st.button("Generate Story, eBook, and Audiobook", key="generate_all"):
        try:
            # Prompt ajustado para gerar a história com capítulos
            prompt = (
                f"Você é um escritor talentoso. Crie uma história com o tom {tone.lower()} baseada "
                f"nas informações abaixo. A história deve incluir um título geral, capítulos com títulos e "
                f"um texto coeso. Cada capítulo deve ter pelo menos 500 palavras. Alguns capítulos podem ter "
                f"mais para enriquecer a narrativa. Use as informações abaixo como base:\n\n"
                f"Informações iniciais: {st.session_state.audio1_text}\n"
                f"Respostas às perguntas: {st.session_state.audio2_text}"
            )
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": prompt}]
            )
            story_content = response["choices"][0]["message"]["content"]
            
            # Separar título e capítulos
            lines = story_content.split("\n")
            st.session_state.story_title = lines[0]  # Título geral
            st.session_state.final_story = "\n".join(lines[1:])  # Texto completo com capítulos
            
            st.success("Story generated successfully!")
            st.markdown(f"### {st.session_state.story_title}")
            st.write(st.session_state.final_story)

            # Geração do eBook usando FPDF2
            pdf = FPDF()
            pdf.add_page()
            
            # Configurar fontes sem o parâmetro "uni"
            font_regular = "fonts/FreeSerif.ttf"
            font_bold = "fonts/FreeSerifBold.ttf"
            pdf.add_font("FreeSerif", style="", fname=font_regular)
            pdf.add_font("FreeSerif", style="B", fname=font_bold)
            
            # Configurar a capa
            pdf.set_font("FreeSerif", "B", size=24)
            pdf.cell(0, 10, f"Título Geral: {st.session_state.story_title}", ln=True, align="C")
            pdf.ln(20)
            
            # Adicionar capítulos ao eBook
            pdf.set_font("FreeSerif", size=14)
            chapters = st.session_state.final_story.split("\n\n")
            for chapter in chapters:
                if chapter.strip():
                    if chapter.startswith("Capítulo") or chapter.startswith("Chapter"):
                        pdf.set_font("FreeSerif", "B", size=16)
                        pdf.ln(10)  # Espaçamento antes do título do capítulo
                        pdf.multi_cell(0, 10, chapter.strip())  # Ajuste automático para a largura da página
                        pdf.ln(5)
                    else:
                        pdf.set_font("FreeSerif", size=12)
                        pdf.multi_cell(0, 10, chapter.strip())  # Ajuste automático para a largura da página
            
            # Salvar e exibir botão de download do eBook
            pdf_output = BytesIO()
            pdf.output(pdf_output)
            pdf_output.seek(0)
            
            st.download_button(
                label="Download eBook (PDF)",
                data=pdf_output,
                file_name="ebook.pdf",
                mime="application/pdf"
            )

            
            # Gerar Audiobook
            tts = gTTS(text=st.session_state.final_story, lang="pt")
            audio_output = BytesIO()
            tts.write_to_fp(audio_output)
            audio_output.seek(0)
            
            # Player e botão de download do audiobook
            st.audio(audio_output, format="audio/mp3")
            st.download_button(
                label="Download Audiobook (MP3)",
                data=audio_output,
                file_name="audiobook.mp3",
                mime="audio/mp3"
            )

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

