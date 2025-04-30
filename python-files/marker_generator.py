import os
import sys

def generate_jsx(video_path):
    base, ext = os.path.splitext(video_path)
    marker_file = base + "_chapters.txt"
    jsx_file = base + "_markers.jsx"

    if not os.path.exists(marker_file):
        print(f"❌ Marker file not found: {marker_file}")
        input("Press Enter to exit...")
        return

    with open(marker_file, "r", encoding="utf-8") as mf:
        lines = mf.readlines()

    with open(jsx_file, "w", encoding="utf-8") as jf:
        jf.write("""/**
 * Auto-generated JSX Marker Script
 * Attach markers to clip in Premiere Pro via JSX Launcher
 */
var project = app.project;
var selectedItems = project.getSelection();

if (!selectedItems || selectedItems.length !== 1) {
    alert("⚠️ Please select ONE video clip in the Project Bin.");
} else {
    var clip = selectedItems[0];
""")

        for line in lines:
            parts = line.strip().split(" ", 1)
            if len(parts) < 2:
                continue
            timecode, label = parts
            h, m, s = map(int, timecode.split(":"))
            total_sec = h * 3600 + m * 60 + s
            jf.write(f'    var marker = clip.createMarker({total_sec});\n')
            jf.write(f'    marker.name = "{label}";\n\n')

        jf.write("    alert('✅ Markers added to clip.');\n}")
    
    print(f"✅ JSX script created: {jsx_file}")
    input("Press Enter to close...")

# Entry point
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("📥 Please drag and drop a video file onto this script.")
        input("Press Enter to close...")
    else:
        generate_jsx(sys.argv[1])
