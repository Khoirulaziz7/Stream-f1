import os
import yt_dlp
import logging
import glob
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Masukkan token bot Telegram Anda
TOKEN = "7170536524:AAHRSLkj7e2KZD7iWYC6Q7_sA2LNBk9S1hk"

# Mengatur logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Halo! Kirimkan saya nama lagu, dan saya akan mencarikannya untuk Anda.")

async def search_music(update: Update, context: CallbackContext) -> None:
    query = update.message.text
    logging.info(f"Pengguna mencari lagu: {query}")
    await update.message.reply_text(f"Mencari: {query}...")

    # Folder untuk menyimpan file
    download_dir = "music"
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'default_search': 'ytsearch1',
        'outtmpl': f'{download_dir}/%(title)s.%(ext)s',  # Menentukan folder dan nama file
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            
            if not info:
                await update.message.reply_text("Tidak dapat menemukan lagu. Coba judul lain.")
                return
            
            # Mencari file yang diunduh di folder music
            downloaded_files = glob.glob(os.path.join(download_dir, "*.mp3"))
            if not downloaded_files:
                await update.message.reply_text("Terjadi kesalahan saat mengunduh file.")
                logging.error("File tidak ditemukan setelah diunduh.")
                return

            downloaded_file = downloaded_files[0]  # Mengambil file MP3 pertama yang ditemukan
            logging.info(f"Nama file yang diharapkan: {downloaded_file}")

            # Memeriksa apakah file ada
            if not os.path.exists(downloaded_file):
                await update.message.reply_text("Terjadi kesalahan saat mengunduh file.")
                logging.error(f"File {downloaded_file} tidak ditemukan setelah diunduh.")
                return

        # Mengirimkan audio
        with open(downloaded_file, "rb") as audio:
            await update.message.reply_audio(audio)

        # Menghapus file setelah dikirim
        os.remove(downloaded_file)
        logging.info(f"File {downloaded_file} berhasil dikirim dan dihapus.")

    except Exception as e:
        logging.error(f"Kesalahan saat mengunduh atau mengirim: {e}")
        await update.message.reply_text(f"Kesalahan: {str(e)}")

def main() -> None:
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_music))

    logging.info("Bot telah berjalan.")
    app.run_polling()

if __name__ == "__main__":
    main()
