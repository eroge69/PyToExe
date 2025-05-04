import zipfile
import io

data = "Halo dunia, ini dari string!"
zip_buffer = io.BytesIO()

with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
    zipf.writestr("hello.txt", data)

with open("hasil.zip", "wb") as f:
    f.write(zip_buffer.getvalue())
