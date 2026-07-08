console.log("JS LOADED ✔");
let selectedRecords = new Map();

function updateSelectedCount() {
    document.getElementById("selectedCount").innerText =
        `${selectedRecords.size} selected`;
}

function downloadCSV() {

    if (selectedRecords.size === 0) {
        alert("No rows selected.");
        return;
    }

    const rows = Array.from(selectedRecords.values());

    // choose columns you want in CSV
    const headers = [
        "id",
        "bacterium_name_formatted",
        "assembly",
        "group",
        "annotation",
        "sequence"
    ];

    let csv = headers.join(",") + "\n";

    rows.forEach(row => {

        const line = headers.map(h => {

            let value = row[h] ?? "";

            // escape quotes
            value = String(value).replace(/"/g, '""');

            return `"${value}"`;
        });

        csv += line.join(",") + "\n";
    });

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });

    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "selected_sequences.csv";

    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    URL.revokeObjectURL(url);
}

document.addEventListener("DOMContentLoaded", () => {
    const dataContainer = document.getElementById("dataContainer");
    
    let currentPage = 1;
    let pageSize = 10;
    let totalPages = 1;
    

    const results = document.getElementById("results");
    const pageInfo = document.getElementById("pageInfo");
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    const clearBtn = document.getElementById("clearBtn");
    const form = document.getElementById("filterForm");

    const downloadBtn = document.getElementById("downloadBtn");

    downloadBtn.addEventListener("click", downloadCSV);
    
    // ------------------------------
    // FETCH DATA
    // ------------------------------
    async function fetchData(page) {
        const bacterium = document.getElementById("bacterium")?.value || "";
        const group = document.getElementById("group")?.value || "";
        const annotation = document.getElementById("annotation")?.value || "";
        const url = `/api/promoter/?page=${page}&page_size=${pageSize}&bacterium=${encodeURIComponent(bacterium)}&group=${encodeURIComponent(group)}&annotation=${encodeURIComponent(annotation)}`;
        const res = await fetch(url);
        const data = await res.json();
        return data;
    }

    // ------------------------------
    // RENDER TABLE
    // ------------------------------
    function renderTable(data) {
        results.innerHTML = "";
        const table = document.createElement("table");
        table.border = "1";
        table.style.width = "100%";
        table.innerHTML = `
            <tr>
                <th>
                    <input type="checkbox" id="selectAll">
                </th>
                <th>Bacterium</th>
                <th>Assembly</th>
                <th>Calibrated Probability</th>
                <th>Group</th>
                <th>Annotation</th>
                <th>Sequence</th>
            </tr>
        `;
        data.results.forEach(row => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>
                    <input
                        type="checkbox"
                        class="record-checkbox"
                        data-id="${row.id}"
                    >
                </td>
                <td>${row.bacterium_name_formatted}</td>
                <td>${row.assembly}</td>
                <td>${row.iso_calibrated_probability}</td>
                <td>${row.group}</td>
                <td>${row.annotation}</td>
                <td>${row.sequence}</td>
            `;
            table.appendChild(tr);
            const checkbox = tr.querySelector(".record-checkbox");
            // restore checked state when changing pages
            checkbox.checked = selectedRecords.has(row.id);
            checkbox.addEventListener("change", (e) => {
                if (e.target.checked) {
                    selectedRecords.set(row.id, row);
                } else {
                    selectedRecords.delete(row.id);
                }
                updateSelectedCount();
            });
        });
        const selectAll = table.querySelector("#selectAll");
    
        // if all rows on page are selected
        selectAll.checked =
            data.results.length > 0 &&
            data.results.every(row => selectedRecords.has(row.id));
        selectAll.addEventListener("change", (e) => {
            const checked = e.target.checked;
            table.querySelectorAll(".record-checkbox").forEach(cb => {
                cb.checked = checked;
                const rowId = parseInt(cb.dataset.id);
                const rowData = data.results.find(r => r.id === rowId);
                if (checked) {
                    selectedRecords.set(rowId, rowData);
                } else {
                    selectedRecords.delete(rowId);
                }
            });
            updateSelectedCount();
        });
        results.appendChild(table);
        updateSelectedCount();
    }
    // ------------------------------
    // LOAD PAGE
    // ------------------------------
    async function loadPage(page) {
        results.innerHTML = "Loading...";
        const data = await fetchData(page);
        dataContainer.style.display = "block";

        currentPage = page;
        totalPages = Math.ceil(data.count / pageSize);

        renderTable(data);

        pageInfo.innerText = `Page ${currentPage} / ${totalPages}`;

        prevBtn.disabled = currentPage <= 1;
        nextBtn.disabled = currentPage >= totalPages;

        const stats = document.getElementById("stats");
        stats.innerHTML = `
            Total promoters: <strong>${data.count}</strong><br>
            Unique bacteria: <strong>${data.stats.unique_bacteria}</strong><br>
            Groups: <strong>${data.stats.unique_groups}</strong>
        `;
    }

    // ------------------------------
    // EVENTS
    // ------------------------------
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        loadPage(1);
    });
    prevBtn.addEventListener("click", () => {
        if (currentPage > 1) {
            loadPage(currentPage - 1);
        }
    });
    nextBtn.addEventListener("click", () => {
        if (currentPage < totalPages) {
            loadPage(currentPage + 1);
        }
    });
    clearBtn.addEventListener("click", () => {

        // reset inputs
        document.getElementById("bacterium").value = "";
        document.getElementById("group").value = "";
        document.getElementById("annotation").value = "";

        // reset pagination state
        currentPage = 1;
        totalPages = 1;

        // clear results
        results.innerHTML = "";

        // reset page info
        pageInfo.innerText = "";

        // disable pagination buttons
        prevBtn.disabled = true;
        nextBtn.disabled = true;
        dataContainer.style.display = "none";
        
        // selected counts
        selectedRecords.clear();
        updateSelectedCount();
    });
    const urlParams = new URLSearchParams(window.location.search);
    const incomingGroup = urlParams.get('group');

    if (incomingGroup) {
        const groupInput = document.getElementById("group");
        if (groupInput) {
            // 1. Visually assign the group name to your filter input form
            groupInput.value = incomingGroup;
            
            // 2. Automatically execute the query pipeline
            loadPage(1);
        }
    }
});