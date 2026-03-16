import streamlit as st
import whisper
import os
import tempfile
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

# FIX: Alamat ImageMagick untuk Linux
os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"

st.set_page_config(page_title="BEJAENAH AI Studio", layout="wide")

@st.cache_resource
def load_model():
    return whisper.load_model("base")

model = load_model()

def process_video(input_path, style_config):
    video = VideoFileClip(input_path)
    audio_path = "temp_audio.mp3"
    video.audio.write_audiofile(audio_path, logger=None)
    
    result = model.transcribe(audio_path)
    
    clips = [video]
    for segment in result['segments']:
        # Gunakan font 'DejaVu-Sans' atau kosongkan agar menggunakan font standar server
        txt = TextClip(
            segment['text'].upper(),
            fontsize=style_config['fontsize'],
            color=style_config['color'],
            method='caption',
            size=(video.w * 0.8, None)
        ).set_start(segment['start']).set_end(segment['end']).set_position(('center', video.h * 0.8))
        
        clips.append(txt)

    result_video = CompositeVideoClip(clips)
    output_path = "hasil_subtitle.mp4"
    result_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=video.fps, preset="ultrafast", logger=None)
    
    video.close()
    return output_path

st.title("🎬 BEJAENAH AI Content Studio")

uploaded_file = st.file_uploader("Upload Video (MP4)", type=["mp4"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(uploaded_file.read())
        if st.button("Generate Subtitle"):
            with st.spinner("Sedang memproses... Harap tunggu (5 menit)"):
                try:
                    # Kita pakai settingan standar agar tidak error font
                    hasil = process_video(tmp.name, {"fontsize": 40, "color": "yellow"})
                    st.video(hasil)
                    with open(hasil, "rb") as f:
                        st.download_button("Download Video", f, file_name="bejaenah_video.mp4")
                except Exception as e:
                    st.error(f"Saran: Jika muncul error 'Security Policy', silakan klik 'Reboot App'. Pesan: {e}")
