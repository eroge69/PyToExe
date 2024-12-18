document.getElementById("upload-btn").addEventListener("click", async () => {
    const fileInput = document.getElementById("file");
    const status = document.getElementById("status");

    if (!fileInput.files.length) {
        status.textContent = "Please select a .py file to upload.";
        return;
    }

    const file = fileInput.files[0];
    if (!file.name.endsWith(".py")) {
        status.textContent = "Only .py files are supported.";
        return;
    }

    status.textContent = "Uploading file...";

    // Convert file to base64
    const reader = new FileReader();
    reader.readAsText(file);
    reader.onload = async () => {
        const content = btoa(reader.result); // Convert file content to base64

        try {
            // Send the file to the backend API (your GitHub Actions workflow)
            const response = await fetch("/upload-file", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    fileName: file.name,
                    content: content,
                }),
            });

            if (response.ok) {
                status.textContent = "File uploaded successfully. Conversion in progress...";
            } else {
                const error = await response.json();
                status.textContent = "Error: " + (error.message || "Failed to upload file.");
            }
        } catch (err) {
            status.textContent = "Error: " + err.message;
        }
    };
});
