import streamlit as st
import os
import openai
from fpdf import FPDF
from io import BytesIO
from gtts import gTTS
from fpdf.enums import XPos, YPos
from streamlit.components.v1 import html
import base64
import json

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

# Função para gravar áudio com HTML/JavaScript
def gravar_audio(identificador):
    html_code = f"""
    <script>
        let mediaRecorder;
        let audioChunks = [];

        function startRecording() {{
            navigator.mediaDevices.getUserMedia({{ audio: true }})
                .then(stream => {{
                    mediaRecorder = new MediaRecorder(stream);
                    mediaRecorder.start();

                    mediaRecorder.ondataavailable = event => {{
                        audioChunks.push(event.data);
                    }};
                }})
                .catch(error => {{
                    alert("Microphone access denied. Please enable it in your browser settings.");
                }});
        }}

        function stopRecording() {{
            mediaRecorder.stop();

            mediaRecorder.onstop = () => {{
                const audioBlob = new Blob(audioChunks, {{ type: 'audio/wav' }});
                const reader = new FileReader();
                reader.readAsDataURL(audioBlob);
                reader.onloadend = () => {{
                    const base64Audio = reader.result.split(',')[1];
                    fetch('/audio_upload_{identificador}', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ audio: base64Audio }})
                    }})
                    .then(response => {{
                        if (response.ok) {{
                            alert("Audio uploaded successfully!");
                        }} else {{
                            alert("Failed to upload audio.");
                        }}
                    }});
                }};
            }};
        }}
    </script>

    <button onclick="startRecording()">Start Recording</button>
    <button onclick="stopRecording()">Stop Recording</button>
    """
    html(html_code, height=200)

# Função para transcrever áudio
def transcrever_audio(audio_base64):
    audio_bytes = BytesIO(base64.b64decode(audio_base64))
    try:
        response = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_bytes
        )
        return response.get("text", "Transcription failed.")
    except Exception as e:
        return str(e)

# Passo 1: Gravação do primeiro áudio
if st.session_state.audio1_text is None:
    st.markdown("### Step 1: Record your story")
    gravar_audio("audio1")

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
    gravar_audio("audio2")

# Passo 4: Gerar história, eBook e audiobook
if st.session_state.audio1_text and st.session_state.audio2_text:
    st.subheader("Generate your story, eBook, and audiobook")
    tone = st.selectbox("Choose the tone of the narration:", ["Neutral", "Dramatic", "Animated", "Suspense"])
    voice = st.radio("Choose the narration voice:", ["Feminina", "Masculina"])

    if st.button("Generate Story, eBook, and Audiobook"):
        try:
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
