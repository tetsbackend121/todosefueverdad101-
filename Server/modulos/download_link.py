from moviepy.editor import VideoFileClip
import pytube
import os

def ConvertMP3(url):
    os.chdir("downloads\mp3")
    resolution = "low"

    def download_video(url, resolution):
        itag = choose_resolution(resolution)
        video = pytube.YouTube(url)
        stream = video.streams.get_by_itag(itag)
        if stream is None:
            raise ValueError(f"No se encontró un stream con el itag {itag}")
        stream.download()
        return stream.default_filename

    def choose_resolution(resolution):
        global otro
        if resolution in ["low", "360", "360p"]:
            otro = 18
        elif resolution in ["medium", "720", "720p", "hd"]:
            otro = 22
        elif resolution in ["high", "1080", "1080p", "fullhd", "full_hd", "full hd"]:
            otro = 137
        elif resolution in ["very high", "2160", "2160p", "4K", "4k"]:
            otro = 313
        else:
            otro = 18
        return otro

    def convert_to_mp3(filename):
        clip = VideoFileClip(filename)
        clip.audio.write_audiofile(filename[:-4] + ".mp3")
        clip.close()

        try:
            os.remove(filename)
            print(f"Archivo {filename} eliminado correctamente.")
        except OSError as e:
            print(f"Error al eliminar el archivo {filename}: {e}")

    filename = download_video(url, resolution)
    convert_to_mp3(filename)

    os.chdir("../..")

    return filename[:-4] + ".mp3"
    

def ConvertMP4(url, resolution):
    os.chdir("downloads\mp4" + "\\" + str(resolution))
    def download_video(url, resolution):
        global otro

        print("Es:" + resolution)
        if resolution == "1080p":
            otro = 137
        elif resolution == "720p":
            otro = 22
        elif resolution == "480p":
            otro = 135
        elif resolution == "360p":
            otro = 18
        elif resolution == "144p":
            otro = 160
        else:
            print("Resolución no soportada, usando 360p por defecto.")
            otro = 22

        video = pytube.YouTube(url)

        available_streams = video.streams.filter(progressive=True)

        print("Stream disponibles:")
        
        for stream in available_streams:
            print(f"itag: {stream.itag}, resolución: {stream.resolution}, mime type: {stream.mime_type}")
        
        stream = video.streams.get_by_itag(otro)
        stream.download()
        return stream.default_filename

    nombre = download_video(url, resolution)
    print(f"Video descargado: ")
    os.chdir("../..")
    os.chdir("..")

    return nombre

# Ejemplo de uso
# ConvertMP3("url_del_video")
# ConvertMP4("url_del_video", "720p")
