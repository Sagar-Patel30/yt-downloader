import streamlit as st
import yt_dlp
import os

st.set_page_config(page_title="YouTube Downloader", page_icon="🎥", layout="centered")

st.title("🎥 YouTube Downloader")
st.write("Download videos or audio from YouTube in the best available quality.")

# Input URL
url = st.text_input("Enter YouTube URL:")

# Choose format
option = st.radio("Select Download Type:", ["Best Video + Audio", "Audio Only (MP3)"])

progress_bar = st.progress(0)
status_text = st.empty()

if url:
    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            st.session_state["video_info"] = info
            st.subheader(info["title"])
            if "thumbnail" in info:
                st.image(info["thumbnail"], width=400)
                st.write(info['resolution'])
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def progress_hook(d):
    if d['status'] == 'downloading':
        if d.get('total_bytes'):
            percent = d['downloaded_bytes'] / d['total_bytes']
            progress_bar.progress(min(percent, 1.0))
            status_text.text(f"⬇️ Downloading... {percent*100:.1f}%")
    elif d['status'] == 'finished':
        progress_bar.progress(1.0)
        status_text.text("✅ Download finished, processing...")

if st.button("Download"):
    if not url.strip():
        st.error("⚠️ Please enter a valid YouTube URL")
    else:
        try:
            if option == "Best Video + Audio":
                ydl_opts = {
                    "format": "bestvideo+bestaudio/best",
                    "merge_output_format": "mp4",
                    "outtmpl": "%(title)s.%(ext)s",
                    "progress_hooks": [progress_hook],
                }
            else:  # Audio Only
                ydl_opts = {
                    "format": "bestaudio/best",
                    "outtmpl": "%(title)s.%(ext)s",
                    "progress_hooks": [progress_hook],
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }],
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

                if option == "Audio Only (MP3)":
                    filename = os.path.splitext(filename)[0] + ".mp3"

            st.success("✅ Download complete!")
            with open(filename, "rb") as f:
                st.download_button("⬇️ Save File", f, file_name=os.path.basename(filename))

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
