import streamlit as st
import whisper
import os
import tempfile
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

# FIX: Paksa server menggunakan path ImageMagick yang benar
os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"

st.set_page_config(page_title="BEJAENAH AI Studio", layout="wide")

@st.cache_resource
def load_model():
    return whisper.load_model("base")

model = load_model()

def process_video(input_path, style):
    video = VideoFileClip(input_path)
    # Ambil audio untuk Whisper
    audio_path = "temp_audio.mp3"
    video.audio.write_audiofile(audio_path, logger=None)
    
    # Transcribe
    result = model.transcribe(audio_path)
    
    clips = [video]
    for segment in result['segments']:
        # Buat teks subtitle sederhana
        txt = TextClip(
            segment['text'].upper(),
            fontsize=style['fontsize'],
            color=style['color'],
            font='Arial-Bold',
            method='caption',
            size=(video.w * 0.8, None)
        ).set_start(segment['start']).set_end(segment['end']).set_position(('center', video.h * 0.8))
        
        clips.append(txt)

    result_video = CompositeVideoClip(clips)
    output_path = "hasil_subtitle.mp4"
    # Gunakan preset 'ultrafast' agar server tidak overload
    result_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=video.fps, preset="ultrafast", logger=None)
    
    video.close()
    return output_path

st.title("🎬 BEJAENAH AI Content Studio")

col1, col2 = st.columns([1, 2])

with col1:
    style_choice = st.selectbox("Style Subtitle:", ["Viral Yellow", "Clean White"])
    styles = {
        "Viral Yellow": {"fontsize": 50, "color": "yellow"},
        "Clean White": {"fontsize": 40, "color": "white"}
    }

with col2:
    uploaded_file = st.file_uploader("Upload Video (MP4)", type=["mp4"])
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(uploaded_file.read())
            if st.button("Generate Subtitle"):
                with st.spinner("Sedang memproses... Harap tunggu (5-10 menit)"):
                    try:
                        hasil = process_video(tmp.name, styles[style_choice])
                        st.video(hasil)
                        with open(hasil, "rb") as f:
                            st.download_button("Download Video Berhasil", f, file_name="bejaenah_video.mp4")
                    except Exception as e:
                        st.error(f"Terjadi kesalahan teknis: {e}")
