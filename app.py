import streamlit as st
from moviepy.editor import VideoFileClip
import librosa
import numpy as np
import os

# Konfigurasi Halaman Web
st.set_page_config(page_title="AI Auto Clipper", page_icon="✂️", layout="centered")

st.title("✂️ AI Auto-Clipper Bola & Game")
st.markdown("Aplikasi ini mendeteksi momen heboh (lonjakan suara) dari video Anda dan otomatis memotongnya menjadi klip pendek!")

# Form Upload Video
uploaded_file = st.file_uploader("Upload Video Podcast/Game Anda (MP4)", type=["mp4"])

if uploaded_file is not None:
    # Simpan file sementara
    with open("temp_video.mp4", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.video("temp_video.mp4")
    
    clip_duration = st.slider("Berapa detik durasi klip yang diinginkan?", 10, 60, 30)
    
    if st.button("Mulai Auto-Clip! 🚀"):
        with st.spinner('Sedang menganalisis momen heboh di video... Ini mungkin memakan waktu.'):
            try:
                # Load video menggunakan MoviePy
                video = VideoFileClip("temp_video.mp4")
                
                # Ekstrak audio untuk dianalisis
                audio_path = "temp_audio.wav"
                video.audio.write_audiofile(audio_path, logger=None)
                
                # Load audio dengan librosa
                y, sr = librosa.load(audio_path, sr=None)
                
                # Hitung energi (volume) dari audio
                rms = librosa.feature.rms(y=y)[0]
                
                # Temukan frame dengan volume tertinggi (momen puncak)
                max_volume_frame = np.argmax(rms)
                peak_time = librosa.frames_to_time(max_volume_frame, sr=sr)
                
                st.success(f"Momen paling heboh ditemukan pada detik ke-{peak_time:.2f}!")
                
                # Tentukan titik potong (misal: 10 detik sebelum momen puncak)
                start_time = max(0, peak_time - (clip_duration * 0.3)) # 30% durasi sebelum puncak
                end_time = min(video.duration, start_time + clip_duration)
                
                st.info(f"Memotong video dari {start_time:.2f} hingga {end_time:.2f}...")
                
                # Potong video
                final_clip = video.subclip(start_time, end_time)
                output_filename = "hasil_clip.mp4"
                final_clip.write_videofile(output_filename, codec="libx264", audio_codec="aac", logger=None)
                
                st.balloons()
                st.success("Klip berhasil dibuat!")
                
                # Tampilkan hasil
                st.video(output_filename)
                
                # Tombol Download
                with open(output_filename, "rb") as file:
                    st.download_button(
                        label="⬇️ Download Hasil Klip",
                        data=file,
                        file_name="auto_clip.mp4",
                        mime="video/mp4"
                    )
                
                # Bersihkan file sementara
                video.close()
                os.remove(audio_path)
                
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")

