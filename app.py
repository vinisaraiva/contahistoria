import streamlit as st
import openai
from io import BytesIO
from gtts import gTTS
import base64

# Configuração da API OpenAI
# openai.api_key = st.secrets["openai_apikey"]

client = OpenAI(
    openai.api_key=os.environ.get("openai_apikey"),
)

# Configuração inicial do Streamlit
st.set_page_config(page_title="Storyme.life", layout="centered", initial_sidebar_state="collapsed")

# Inicializando estados da aplicação
if "audio1_text" not in st.session_state:
    st.session_state.audio1_text = None
if "audio2_text" not in st.session_state:
    st.session_state.audio2_text = None
if "final_story" not in st.session_state:
    st.session_state.final_story = None
if "narration_voice" not in st.session_state:
    st.session_state.narration_voice = "Feminina"

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
        audio_file = BytesIO(audio1.read())  # Obtendo os bytes do áudio
        try:
            # Simulação de atribuição de nome, caso necessário
            audio_file.name = "audio1.wav"  # Nome fictício, caso o processo precise de um nome
    
            # Exemplo: Envio para API Whisper
            response = openai.Audio.transcribe("whisper-1", audio_file)
            st.session_state.audio1_text = response.get("text", "Transcription failed.")
            st.success("Audio processed successfully!")
            st.write(f"Transcription: {st.session_state.audio1_text}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Passo 2: Gravação do segundo áudio para responder perguntas
if st.session_state.audio1_text:
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
            st.write(f"Transcription: {st.session_state.audio2_text}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Passo 3: Gerar a história final
if st.session_state.audio1_text and st.session_state.audio2_text:
    st.subheader("Step 3: Generate your final story")
    if st.button("Generate Story"):
        try:
            prompt = (
                "Você é um grande escritor e contador de história, crie uma história interessante "
                "baseado nas informações que acabou de receber:\n"
                f"Informações iniciais: {st.session_state.audio1_text}\n"
                f"Respostas às perguntas: {st.session_state.audio2_text}"
            )
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": prompt}]
            )
            st.session_state.final_story = response["choices"][0]["message"]["content"]
            st.success("Story generated successfully!")
            st.markdown(f"### Final Story:\n{st.session_state.final_story}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Passo 4: Escolher voz e gerar o audiobook
if st.session_state.final_story:
    st.subheader("Step 4: Generate your audiobook")
    
    # Escolher voz
    st.radio("Choose the narration voice:", ["Feminina", "Masculina"], key="narration_voice")

    if st.button("Generate Audiobook"):
        try:
            # Simulação de vozes com gTTS
            if st.session_state.narration_voice == "Feminina":
                tts = gTTS(st.session_state.final_story, lang="pt")
            else:
                # Alterando pitch para voz "masculina" (gTTS não suporta diretamente)
                tts = gTTS(st.session_state.final_story, lang="pt", slow=True)
            
            # Salvando o áudio
            tts.save("audiobook.mp3")
            with open("audiobook.mp3", "rb") as file:
                audio_bytes = file.read()
            st.audio(audio_bytes, format="audio/mp3")
            st.success("Audiobook generated successfully!")

            # Link para download
            st.download_button("Download Audiobook", data=audio_bytes, file_name="audiobook.mp3", mime="audio/mp3")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    
    # Passo 5: Download da história como PDF
    st.subheader("Download your story as a PDF")
    if st.button("Download Story as PDF"):
        try:
            # Gerar PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, st.session_state.final_story)
            pdf_output = BytesIO()
            pdf.output(pdf_output)
            pdf_output.seek(0)

            # Botão de download do PDF
            st.download_button(
                label="Download PDF",
                data=pdf_output,
                file_name="story.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

