import streamlit as st
import whisper
import os
import tempfile
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

# Menggunakan path standar Linux
os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"

st.set_page_config(page_title="BEJAENAH AI Studio", layout="wide")

@st.cache_resource
def load_model():
    return whisper.load_model("base")

model = load_model()

def process_video(input_path, color, fontsize):
    video = VideoFileClip(input_path)
    
    # Kecilkan video agar tidak overload memori
    if video.w > 720:
        video = video.resize(width=720)

    audio_path = "temp_audio.mp3"
    video.audio.write_audiofile(audio_path, logger=None)
    
    # AI Transcribe
    result = model.transcribe(audio_path)
    
    clips = [video]
    for segment in result['segments']:
        # Method 'caption' dengan parameter minimal agar lolos Security Policy
        try:
            txt = TextClip(
                segment['text'].upper(),
                fontsize=fontsize,
                color=color,
                method='caption',
                size=(video.w * 0.8, None)
            ).set_start(segment['start']).set_end(segment['end']).set_position(('center', video.h * 0.8))
            clips.append(txt)
        except:
            continue

    result_video = CompositeVideoClip(clips)
    output_path = "bejaenah_output.mp4"
    
    # Gunakan preset tercepat agar server tidak crash
    result_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24, preset="ultrafast", logger=None)
    
    video.close()
    return output_path

st.title("🎬 BEJAENAH AI Content Studio")

with st.sidebar:
    st.header("Pengaturan")
    color_choice = st.selectbox("Warna Teks:", ["Yellow", "White", "Cyan"])
    size_choice = st.slider("Ukuran Teks:", 20, 70, 40)

uploaded_file = st.file_uploader("Upload Video (MP4)", type=["mp4"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(uploaded_file.read())
        if st.button("Generate Subtitle Sekarang"):
            with st.spinner("Sedang memproses video Anda..."):
                try:
                    hasil = process_video(tmp.name, color_choice.lower(), size_choice)
                    st.video(hasil)
                    with open(hasil, "rb") as f:
                        st.download_button("📥 Download Video Hasil", f, file_name="bejaenah_video.mp4")
                except Exception as e:
                    st.error(f"Terjadi kendala teknis: {e}")
