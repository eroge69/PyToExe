import argparse
import cv2
import time
import os
import shutil
from datetime import datetime, timedelta

parser = argparse.ArgumentParser(description="Snapshot script for TE-1700 and TC-1000.")
parser.add_argument("--ip_address", '-ip', required=False, type=str, default="172.16.210.200", help="IP address of the camera (default: 172.16.210.200)")
parser.add_argument("--username", '-uname', required=False, type=str, default="Controls", help="Username of the camera (default: Controls)")
parser.add_argument("--password", '-pswd', required=False, type=str, default="Controls", help="Password of the camera (default: Controls)")
parser.add_argument("--rtsp_port", '-rp', required=False, type=int, default=554, help="RTSP port (default: 554)")
parser.add_argument("--stream_id", '-sid', required=False, type=int, default=1, help="Stream ID to capture images from (default: 1)")
parser.add_argument("--show", '-s', action="store_true", help="Display the captured frame")
parser.add_argument("--dir", '-d', required=False, type=str, default="C:/tmp/OpenCV", help="Storage Path (default: C:/tmp/OpenCV)")
parser.add_argument("--interval", '-i', required=False, type=int, default=10, help="Script Interval (default: 10 minutes")
parser.add_argument("--cap_interval", '-ci', required=False, type=int, default=20, help="Capture Interval (default: 20 seconds)")
parser.add_argument("--free_storage", '-fs', required=False, type=int, default=15, help="Min free storage allowed before deleting old files (default: 15%%)")
parser.add_argument("--del_days", '-dd', required=False, type=int, default=30, help="When storage low, delete files older than x days of data (default: 30)")
parser.add_argument("--test_del", '-t', required=False, type=str, default="N", help="Option to test file deletion prior to actioning Y/N (default: N)")
parser.add_argument("--site_name", '-sname', required=False, type=str, default="frame", help="Site/File name prefix (default: frame)")
args = parser.parse_args()

ip_camera_url = "rtsp://{username}:{password}@{ip_address}:{rtsp_port}/snl/live/1/{stream_id}".format(
    username=args.username,
    password=args.password,
    ip_address=args.ip_address,
    rtsp_port=args.rtsp_port,
    stream_id=args.stream_id
)

# Define the directory to check and clean
directory_path = args.dir
# Set flag for real or test delete process
test_delete = args.test_del
filename_prefix = args.site_name

# Define the threshold for free disk space (15%)
threshold_percent = args.free_storage

# Get the total and available disk space
total_space, _, available_space = shutil.disk_usage(directory_path)

# Calculate the free space percentage
free_space_percent = (available_space / total_space) * 100

# Define the maximum age of files to delete (30 days)
max_age_days = args.del_days

# Define capture interval and script call intervals
image_interval = args.cap_interval  # default: 20 seconds
script_call_intv = args.interval  # default: 10 minutes

def capture_frames(ip_camera_url, output_directory):
    retry_attempts = 3
    retry_interval = 2  # seconds
    iterate_count = (script_call_intv * 60) / image_interval

    while iterate_count > 0:
        try:
            print(iterate_count)
            iterate_count -= 1
            start_time = time.time()
            cap = cv2.VideoCapture(ip_camera_url)

            ret, frame = cap.read()
            if not ret:
                raise Exception("Error reading frame from IP camera")

            # Save the frame to the specified directory
            timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")

            # Save the file directly in the output directory
            filename = f"{output_directory}/{filename_prefix}_{timestamp}.png"
            cv2.imwrite(filename, frame)

            print(f"Saved frame as {filename}")

            if free_space_percent < threshold_percent:
                print(f"Free disk space is less than {threshold_percent}% ({free_space_percent:.2f}%)")

                # Get the current date
                current_date = datetime.now()

                # Iterate over files in the directory
                for filename in os.listdir(directory_path):
                    file_path = os.path.join(directory_path, filename)

                    # Check if the file is older than max_age_days
                    file_modified_date = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if (current_date - file_modified_date) >= timedelta(days=max_age_days):
                        if test_delete == "N":
                            # Delete the file
                            os.remove(file_path)
                            print(f"Deleted {filename} (last modified: {file_modified_date})")
                        else:
                            print(f"Test Delete {filename} (last modified: {file_modified_date})")

            else:
                print(f"Free disk space is greater than {threshold_percent}% ({free_space_percent:.2f}%)")

            # Release the camera connection
            cap.release()

            # Wait for the remaining time before capturing the next frame
            end_time = time.time()
            elapsed_time = end_time - start_time
            sleep_time = (image_interval - elapsed_time)
            if iterate_count > 0:
                time.sleep(sleep_time)

        except Exception as e:
            print(f"Error: {e}")
            # Retry the connection
            retry_attempts -= 1
            if retry_attempts <= 0:
                print("Max retry attempts reached. Exiting.")
                break
            print(f"Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)

if __name__ == "__main__":
    try:
        capture_frames(ip_camera_url, directory_path)
    except KeyboardInterrupt:
        print("User interrupted. Exiting.")
    except Exception as e:
        print(f"Error: {e}")