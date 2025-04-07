import pyodbc
import base64
from PIL import Image
from minio import Minio
import io
import uuid
from tqdm import tqdm
import logging
import configparser
import schedule
import time
from datetime import datetime

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Database configuration
MSSQL_CONN_STR = (
    f"DRIVER={{{config['Database']['Driver']}}};"
    f"SERVER={config['Database']['Server']};"
    f"DATABASE={config['Database']['Database']};"
    f"UID={config['Database']['UID']};"
    f"PWD={config['Database']['PWD']};"
)

# MinIO configuration
MINIO_CLIENT = Minio(
    config['MinIO']['Endpoint'],
    access_key=config['MinIO']['AccessKey'],
    secret_key=config['MinIO']['SecretKey'],
    secure=False
)

BUCKET_NAME = config['MinIO']['BucketName']
BATCH_SIZE = int(config['Settings']['BatchSize'])

# Ensure the bucket exists
if not MINIO_CLIENT.bucket_exists(BUCKET_NAME):
    MINIO_CLIENT.make_bucket(BUCKET_NAME)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def convert_and_upload_screen(row):
    screen_bytes = row.Screen
    if not screen_bytes:
        return None

    try:
        img = Image.open(io.BytesIO(screen_bytes))
        buffer = io.BytesIO()
        img.save(buffer, format="WEBP", quality=80)
        buffer.seek(0)

        object_name = f"{row.IncidentID}/{row.AlertID or uuid.uuid4()}.webp"
        MINIO_CLIENT.put_object(
            BUCKET_NAME,
            object_name,
            buffer,
            length=-1,
            part_size=10 * 1024 * 1024,
            content_type="image/webp"
        )
        return object_name
    except Exception as e:
        logging.warning(f"Ошибка обработки скриншота AlertID {row.AlertID}: {e}")
        return None

def process_batch(cursor, insert_cursor, batch):
    for row in batch:
        minio_key = convert_and_upload_screen(row)
        if minio_key:
            insert_cursor.execute("""
                INSERT INTO dbo.MaterializedTable_Links (
                    AlertTime, IncidentID, DisplayName, InterceptUser, GroupName,
                    AlertName, SearchSummary, Activity, Process, ScreenURL, DBDATE,
                    AlertID, ResultRel, InterceptPCName, DocumentName, DocumentExt,
                    DocumentSize, from_addr, from_name, to_addr
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row.AlertTime, row.IncidentID, row.DisplayName, row.InterceptUser, row.GroupName,
                row.AlertName, row.SearchSummary, row.Activity, row.Process,
                f"http://{config['MinIO']['Endpoint']}/{BUCKET_NAME}/{minio_key}",
                row.DBDATE, row.AlertID, row.ResultRel, row.InterceptPCName,
                row.DocumentName, row.DocumentExt, row.DocumentSize,
                row.from_addr, row.from_name, row.to_addr
            ))

def stream_process():
    conn = pyodbc.connect(MSSQL_CONN_STR)
    conn2 = pyodbc.connect(MSSQL_CONN_STR)
    cursor = conn.cursor()
    insert_cursor = conn2.cursor()

    # Count total rows
    cursor.execute("SELECT COUNT(*) FROM dbo.MaterializedTable")
    total = cursor.fetchone()[0]

    logging.info(f"Всего строк для обработки: {total}")
    offset = 0

    with tqdm(total=total, desc="Обработка") as pbar:
        while offset < total:
            cursor.execute(f"""
                SELECT AlertTime, IncidentID, DisplayName, InterceptUser, GroupName,
                       AlertName, SearchSummary, Activity, Process, Screen, DBDATE,
                       AlertID, ResultRel, InterceptPCName, DocumentName, DocumentExt,
                       DocumentSize, from_addr, from_name, to_addr
                FROM dbo.MaterializedTable
                ORDER BY AlertTime DESC
                OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
            """, offset, BATCH_SIZE)

            rows = cursor.fetchall()
            if not rows:
                break

            process_batch(cursor, insert_cursor, rows)
            conn2.commit()
            offset += len(rows)
            pbar.update(len(rows))

    cursor.close()
    insert_cursor.close()
    conn.close()
    conn2.close()

    logging.info("✅ Обработка завершена")

# Scheduler setup
start_time = config['Scheduler']['StartTime']
interval = config['Scheduler']['Interval']

if interval == "daily":
    schedule.every().day.at(start_time).do(stream_process)
elif interval == "hourly":
    schedule.every().hour.at(":00").do(stream_process)  # Runs at the start of every hour
elif interval == "minutely":
    schedule.every().minute.at(":00").do(stream_process)  # Runs at the start of every minute

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    logging.info(f"Scheduler started. Next run at {start_time} ({interval}).")
    run_scheduler()
