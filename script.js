document.getElementById("upload-btn").addEventListener("click", async () => {
    const fileInput = document.getElementById("file");
    const status = document.getElementById("status");
    const downloadLinkContainer = document.getElementById("download-link-container");

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
    downloadLinkContainer.innerHTML = ""; // Clear previous download links

    const reader = new FileReader();
    reader.readAsText(file);
    reader.onload = async () => {
        const content = btoa(reader.result); // Convert file content to base64

        try {
            const response = await fetch(
                "https://api.github.com/repos/eroge69/PyToExe/contents/uploads/" + file.name,
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

                // Polling for the status of the conversion or instructing user to check Actions page
                const checkConversionStatus = setInterval(async () => {
                    const actionRunStatus = await fetch(
                        "https://api.github.com/repos/eroge69/PyToExe/actions/runs"
                    );
                    const actionData = await actionRunStatus.json();
                    const latestRun = actionData.workflow_runs[0];

                    if (latestRun.status === "completed" && latestRun.conclusion === "success") {
                        clearInterval(checkConversionStatus); // Stop polling
                        status.textContent = "Conversion completed!";

                        // Provide download link for the EXE file
                        const exeDownloadLink = `https://github.com/eroge69/PyToExe/actions/artifacts/${latestRun.id}/converted-exe`;
                        downloadLinkContainer.innerHTML = `<a href="${exeDownloadLink}" target="_blank">Download EXE</a>`;
                    } else if (latestRun.status === "completed" && latestRun.conclusion === "failure") {
                        clearInterval(checkConversionStatus);
                        status.textContent = "Conversion failed. Please try again later.";
                    }
                }, 5000); // Poll every 5 seconds to check conversion status
            } else {
                const error = await response.json();
                status.textContent = "Error: " + (error.message || "Failed to upload file.");
            }
        } catch (err) {
            status.textContent = "Error: " + err.message;
        }
    };
});
