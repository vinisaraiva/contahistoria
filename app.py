import streamlit as st
import openai
from io import BytesIO
from gtts import gTTS
import base64

# Configurando a API da OpenAI
openai.api_key = openai_apikey

# Configuração do Streamlit
st.set_page_config(page_title="Storyme.life", layout="centered", initial_sidebar_state="collapsed")

# Inicializando estado da aplicação
if "audio1_text" not in st.session_state:
    st.session_state.audio1_text = None
if "questions" not in st.session_state:
    st.session_state.questions = None
if "audio2_text" not in st.session_state:
    st.session_state.audio2_text = None
if "final_story" not in st.session_state:
    st.session_state.final_story = None

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

# Passo 1: Gravação do primeiro áudio
if st.session_state.audio1_text is None:
    st.markdown('<div class="microphone-icon">🎤</div>', unsafe_allow_html=True)
    audio1 = st.audio_input("🎙️ Click below to record your story:")
    if audio1 is not None:
        st.write("Processing your audio...")
        audio_file = BytesIO(audio1.read())
        try:
            # Enviando áudio para API Whisper
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
            # Geração de perguntas
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

    # Botão para gravar segundo áudio
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    audio2 = st.audio_input("🎙️ Record your answers below:")
    if audio2 is not None:
        st.write("Processing your audio answers...")
        audio_file = BytesIO(audio2.read())
        try:
            # Transcrevendo o segundo áudio
            response = openai.Audio.transcribe("whisper-1", audio_file)
            st.session_state.audio2_text = response.get("text", "Transcription failed.")
            st.success("Answers processed successfully!")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

# Passo 3: Gerar a história final
if st.session_state.audio1_text and st.session_state.audio2_text:
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    if st.button("Generate Story"):
        try:
            # Gerando a história final
            prompt = f"Combine the following inputs to create a story with more than 4 chapters and at least 1500 characters:\nAudio 1: {st.session_state.audio1_text}\nAudio 2: {st.session_state.audio2_text}"
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": prompt}]
            )
            st.session_state.final_story = response["choices"][0]["message"]["content"]
            st.success("Story generated successfully!")
            st.markdown(f"### Final Story:\n{st.session_state.final_story}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

# Mensagem final
st.markdown('</div>', unsafe_allow_html=True)
