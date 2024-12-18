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
            // Create a new file in the 'uploads' folder using GitHub API
            const response = await fetch(
                "https://api.github.com/repos/your-username/python-to-exe/contents/uploads/" + file.name,
                {
                    method: "PUT",
                    headers: {
                        "Authorization": "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",
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        message: "Upload " + file.name,
                        content: content,
                    }),
                }
            );

            if (response.ok) {
                status.textContent = "File uploaded successfully. Conversion in progress...";
                // Wait for Actions to finish (optional: Polling or provide instructions to check Actions page)
            } else {
                const error = await response.json();
                status.textContent = "Error: " + (error.message || "Failed to upload file.");
            }
        } catch (err) {
            status.textContent = "Error: " + err.message;
        }
    };
});
