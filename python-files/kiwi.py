from moviepy.editor import ImageSequenceClip

def gerar_video():
    # Lista de imagens (deve estar no mesmo diretório ou informar o caminho)
    imagens = ["frame1.png", "frame2.png", "frame3.png"]

    # Cria o clipe com FPS definido
    clip = ImageSequenceClip(imagens, fps=12)

    # Exporta o vídeo final
    clip.write_videofile("video_gerado.mp4")

# Chamada da função
if __name__ == "__main__":
    gerar_video()
