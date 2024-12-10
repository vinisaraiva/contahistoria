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
# Passo 4: Gerar a história final com opções de tom e voz
if st.session_state.audio1_text and st.session_state.audio2_text:
    st.subheader("Generate your final story")
    
    # Escolha do tom da narração
    tone = st.selectbox(
        "Choose the tone of the narration:",
        ["Neutral", "Dramatic", "Animated", "Suspense"],
        key="narration_tone"
    )
    
    # Escolha da voz
    st.radio("Choose the narration voice:", ["Feminina", "Masculina"], key="narration_voice")

    if st.button("Generate Story"):
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
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    # Passo 5: Geração do eBook com estrutura de capítulos
    if st.session_state.final_story:
        st.subheader("Download your eBook as PDF")
        if st.button("Download eBook"):
            try:
                # Caminho para as fontes Unicode
                font_dir = "fonts/"
                font_regular = os.path.join(font_dir, "FreeSerif.ttf")
                font_bold = os.path.join(font_dir, "FreeSerifBold.ttf")

                # Criar o PDF
                pdf = FPDF()
                pdf.add_page()

                # Configurar a capa
                pdf.add_font("FreeSerif", "", font_regular, uni=True)
                pdf.add_font("FreeSerif", "B", font_bold, uni=True)
                pdf.set_font("FreeSerif", "B", size=24)
                pdf.multi_cell(0, 10, st.session_state.story_title, align="C")
                pdf.ln(20)

                # Dividir a história em capítulos
                chapters = st.session_state.final_story.split("\n\n")
                pdf.add_page()

                # Adicionar capítulos ao corpo do PDF
                pdf.set_font("FreeSerif", size=14)
                for chapter in chapters:
                    if chapter.strip():  # Ignorar linhas em branco
                        if chapter.startswith("Capítulo") or chapter.startswith("Chapter"):
                            pdf.set_font("FreeSerif", "B", size=16)
                            pdf.ln(10)  # Espaçamento antes do título do capítulo
                            pdf.multi_cell(0, 10, chapter.strip())
                            pdf.ln(5)
                        else:
                            pdf.set_font("FreeSerif", size=12)
                            pdf.multi_cell(0, 10, chapter.strip())

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
    # Passo 5: Geração do Audiobook com TTS da OpenAI
    if st.session_state.final_story:
        st.subheader("Generate and download your audiobook")
        if st.button("Generate Audiobook"):
            try:
                # Usando Text-to-Speech da OpenAI
                tts_response = openai.Audio.create(
                    text=st.session_state.final_story,
                    voice=st.session_state.narration_voice.lower(),  # 'feminina' ou 'masculina'
                    tone=st.session_state.narration_tone.lower()  # Tom selecionado
                )
                audio_data = BytesIO(tts_response["audio_content"])
                audio_data.seek(0)

                # Player e botão de download
                st.audio(audio_data, format="audio/mp3")
                st.success("Audiobook generated successfully!")
                
                # Adicionando o botão para download em formato MP3
                st.download_button(
                    label="Download Audiobook",
                    data=audio_data,
                    file_name="audiobook.mp3",
                    mime="audio/mp3"
                )
            except Exception as e:
                st.error(f"An error occurred while generating the audiobook: {str(e)}")

