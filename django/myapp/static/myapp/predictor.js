console.log("Predictor JS loaded ✔");

function cleanFasta(raw) {
    return raw
        .split("\n")
        .filter(line => line.trim() && !line.trim().startsWith(">"))
        .join("")
        .toUpperCase();
}

//read uplloaded file
function readUploadedFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = (e) => reject(new Error("Error reading file"));
        reader.readAsText(file);
    });
}
//cLEAR BUTTON

function clearPrediction() {
    document.getElementById("fastaInput").value = "";
    
    const fileInput = document.getElementById("id_fasta_file");
    if (fileInput) {
        fileInput.value = ""; 
    }

    document.getElementById("results-content").innerHTML = "Results will be shown here.";
    
    document.getElementById("results-card").style.display = "none";
}

//MAIN ENTRY

async function runPrediction() {
    const textInput = document.getElementById("fastaInput").value;
    
    const fileInput = document.getElementById("id_fasta_file"); 
    
    const resultBox = document.getElementById("results-content");
    const card = document.getElementById("results-card");

    let fastaData = "";

    // 1. Determine data source: Prioritize the uploaded file, fallback to text input
    if (fileInput && fileInput.files && fileInput.files.length > 0) {
        try {
            const selectedFile = fileInput.files[0];
            fastaData = await readUploadedFile(selectedFile);
        } catch (err) {
            card.style.display = "block";
            resultBox.innerHTML = `<div style="color:red;">Failed to read uploaded file.</div>`;
            return;
        }
    } else if (textInput && textInput.trim().length > 0) {
        fastaData = textInput;
    }

    // 2. Validate that we actually have content to send
    if (!fastaData || fastaData.trim().length === 0) {
        card.style.display = "block";
        resultBox.innerHTML = `<div style="color:red;">Please enter a FASTA sequence or upload a file</div>`;
        return;
    }

    card.style.display = "block";
    resultBox.innerHTML = "Running prediction...";

    try {
        const response = await fetch("/api/predict/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({ fasta: fastaData }) // Sends raw file text or raw textbox text
        });

        console.log("HTTP STATUS:", response.status);

        if (!response.ok) {
            const errText = await response.text();
            console.error(errText);
            resultBox.innerHTML = `<div style="color:red;">Server error (${response.status})</div>`;
            return;
        }

        const data = await response.json();
        console.log("RESPONSE:", data);

        renderResults(data);

    } catch (err) {
        console.error(err);
        resultBox.innerHTML = `<div style="color:red;">Error contacting server</div>`;
    }
}

//RESULTS TABLE

function renderResults(data) {
    const box = document.getElementById("results-content");

    if (!data || !data.results) {
        box.innerHTML = `<div style="color:red;">Invalid response</div>`;
        return;
    }

    const rows = data.results;

    // 1. Check if any row in the dataset contains an error
    const hasErrors = rows.some(r => r.error);

    // 2. Conditionally include the Status header
    let html = `
        <table style="width:100%; border-collapse: collapse;">
            <thead>
                <tr style="text-align:left; border-bottom:2px solid #ddd;">
                    <th style="padding:8px;">Header</th>
                    <th style="padding:8px;">Sequence</th>
                    <th style="padding:8px;">Length</th>
                    <th style="padding:8px;">Start</th>
                    <th style="padding:8px;">End</th>
                    <th style="padding:8px;">Score</th>
                    <th style="padding:8px;">Flag</th>
                    ${hasErrors ? '<th style="padding:8px;">Status</th>' : ''}
                </tr>
            </thead>
            <tbody>
    `;

    for (const r of rows) {
        const score = r.final_score ?? r.score ?? null;
        const flag = r.flag ?? "-";
        const mode = r.mode ?? "-";
        const seqLength = r.length ?? 0;
        
        // Extract start and end coordinates
        const start = r.peak_window?.start ?? null;
        const end = r.peak_window?.end ?? null;

        const isLength80 = Number(seqLength) === 80;

        // 3. Determine what sequence to show
        let displaySequence = r.sequence ?? "-";
        
        if (r.sequence) {
            if (isLength80) {
                // If length is exactly 80, display the entire sequence intact
                displaySequence = r.sequence;
            } else if (start !== null && end !== null) {
                // Otherwise, slice it to the coordinate window
                displaySequence = r.sequence.slice(start - 1, end);
            }
        }

        // Optional: Highlight rows that are length 80
        const rowBgColor = isLength80 ? "background-color: #f1f8ff;" : ""; 
        const lengthStyle = isLength80 ? "font-weight: bold; color: #0366d6;" : "";

        html += `
            <tr style="border-bottom:1px solid #eee; ${rowBgColor}">
                <td style="padding:8px; font-family:monospace;">
                    ${r.header ?? "-"}
                </td>

                <td style="padding:8px; font-family:monospace; word-break:break-all; max-width:300px;">
                    ${displaySequence}
                </td>

                <td style="padding:8px; ${lengthStyle}">
                    ${seqLength}
                </td>

                <td style="padding:8px;">
                    ${start ?? "-"}
                </td>

                <td style="padding:8px;">
                    ${end ?? "-"}
                </td>

                <td style="padding:8px;">
                    <b>${score !== null ? Number(score).toFixed(4) : "-"}</b>
                </td>

                <td style="padding:8px;">
                    <b>${flag}</b>
                </td>
        `;

        // 4. Conditionally include the Status cell for every row
        if (hasErrors) {
            const statusContent = r.error 
                ? `<span style="color: #dc3545; font-weight: bold;">${r.error}</span>` 
                : "-";
            
            html += `
                <td style="padding:8px;">
                    ${statusContent}
                </td>
            `;
        }

        html += `</tr>`;
    }

    html += `</tbody></table>`;
    box.innerHTML = html;
}


function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : "";
}

// DOWNLOAD AS CSV BUTTON

function downloadTableAsCSV() {
    // 1. Locate the table inside the results area
    const table = document.querySelector("#results-content table");
    if (!table) {
        alert("No results table found to download.");
        return;
    }

    const csvRows = [];
    const rows = table.querySelectorAll("tr");

    for (const row of rows) {
        const csvCells = [];
        // Target both header cells (th) and data cells (td)
        const cells = row.querySelectorAll("th, td");

        for (const cell of cells) {
            // Clean up multi-line spaces, tabs, checkmarks, etc.
            let text = cell.innerText.trim();
            
            // Remove checkmarks or special visual characters if you don't want them in raw data
            text = text.replace("✓", "").trim(); 

            // Escape double quotes inside the string to prevent breaks in standard CSV sheets
            text = text.replace(/"/g, '""');

            // Wrap values containing commas or quotes in double quotes
            if (text.includes(",") || text.includes("\n") || text.includes('"')) {
                csvCells.push(`"${text}"`);
            } else {
                csvCells.push(text);
            }
        }
        
        // Combine cells into a single comma-separated row string
        csvRows.push(csvCells.join(","));
    }

    // 2. Convert array to full CSV multiline string payload
    const csvContent = csvRows.join("\n");

    // 3. Create a Blob (Binary Large Object) for the text data
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);

    // 4. Trigger an invisible download link anchor
    const link = document.createElement("a");
    link.setAttribute("href", url);
    
    // Generate a contextual filename with a clean timestamp descriptor
    const timestamp = new Date().toISOString().slice(0, 10);
    link.setAttribute("download", `fasta_predictions_${timestamp}.csv`);
    
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    
    // Cleanup reference memory
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}