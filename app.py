import streamlit as st
import os
import openai
from fpdf import FPDF
from io import BytesIO
from gtts import gTTS
from fpdf.enums import XPos, YPos  # Importação necessária para substituir o parâmetro "ln"
import textwrap
from st_audio_recorder import audio_recorder


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
# Passo 1: Gravação do primeiro áudio
if st.session_state.audio1_text is None:
    st.markdown("### Step 1: Record your story")
    st.write("Press the button below to start recording.")
    
    # Usar o componente de gravação de áudio
    audio_data = audio_recorder()
    
    if audio_data:
        st.success("Audio recorded successfully!")
        st.audio(audio_data, format="audio/wav")

        # Processar o áudio para transcrição
        st.write("Transcribing your audio...")
        try:
            audio_file = BytesIO(audio_data)
            response = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file
            )
            st.session_state.audio1_text = response.get("text", "Transcription failed.")
            st.success("Audio processed successfully!")
            st.write(f"Transcription: {st.session_state.audio1_text}")
        except Exception as e:
            st.error(f"An error occurred during transcription: {str(e)}")


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
# Passo 3: Gravação do segundo áudio
if st.session_state.questions:
    st.markdown("### Step 2: Record your answers")
    st.write("Press the button below to start recording your answers.")

    # Usar o componente de gravação de áudio
    audio_data = audio_recorder()
    
    if audio_data:
        st.success("Audio recorded successfully!")
        st.audio(audio_data, format="audio/wav")

        # Processar o áudio para transcrição
        st.write("Transcribing your answers...")
        try:
            audio_file = BytesIO(audio_data)
            response = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file
            )
            st.session_state.audio2_text = response.get("text", "Transcription failed.")
            st.success("Answers processed successfully!")
            st.write(f"Transcription: {st.session_state.audio2_text}")
        except Exception as e:
            st.error(f"An error occurred during transcription: {str(e)}")


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
            # Função auxiliar para forçar quebras de texto
            def safe_text_wrap(text, max_width):
                """
                Quebra o texto em linhas menores para caber no espaço disponível no PDF.
                :param text: Texto original.
                :param max_width: Largura máxima da célula em caracteres.
                :return: Texto quebrado em linhas.
                """
                wrapped_lines = []
                for line in text.split("\n"):
                    wrapped_lines.extend(wrap(line, max_width))
                return "\n".join(wrapped_lines)
            
            # Geração do eBook usando FPDF2
            # Função para criar PDF do eBook
            def criar_pdf_e_book(titulo, historia):
                pdf_buffer = BytesIO()
                c = canvas.Canvas(pdf_buffer, pagesize=letter)
                width, height = letter
            
                # Adicionar título do eBook na capa
                c.setFont("Helvetica-Bold", 20)
                c.drawCentredString(width / 2.0, height - 50, titulo)
            
                # Adicionar espaço entre a capa e os capítulos
                c.showPage()
            
                # Configurar fonte e início dos capítulos
                c.setFont("Helvetica", 12)
                margin_x = 72
                margin_y = height - 72
            
                # Adicionar capítulos da história
                for chapter in historia.split("\n\n"):
                    wrapped_text = textwrap.fill(chapter.strip(), 85)  # Limite de 85 caracteres por linha
                    text_object = c.beginText(margin_x, margin_y)
                    text_object.textLines(wrapped_text)
                    c.drawText(text_object)
                    margin_y -= 150  # Controle de espaço entre capítulos
                    if margin_y < 72:  # Criar nova página quando o espaço vertical acabar
                        c.showPage()
                        margin_y = height - 72
            
                # Finalizar o PDF
                c.showPage()
                c.save()
                pdf_buffer.seek(0)
                return pdf_buffer
            
            # Exemplo de uso no Streamlit
            if st.session_state.final_story:
                pdf_output = criar_pdf_e_book(st.session_state.story_title, st.session_state.final_story)
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

