# prompt: Do the same as above, but make a link for the user to click to download the file to the PC. Always reinstall dependencies. Open the interface in new tab (if possible).

import yt_dlp
import gradio as gr
from google.colab import files

# Install necessary libraries if not already installed.
!pip install --upgrade yt-dlp
!pip install --upgrade gradio


def download_video(link):
    ydl_opts = {}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            filename = ydl.prepare_filename(info_dict)
            ydl.download([link])
        return f"Download complete! You can download the file: {filename}"
    except Exception as e:
        return f"Error: {e}"

iface = gr.Interface(
    fn=download_video,
    inputs=gr.Textbox(label="Insert Video Link"),
    outputs=gr.Textbox(label="Status"),
    title="YouTube Video Downloader",
    description="Download YouTube videos in the best available quality."
)

iface.launch(share=True, debug=True)
