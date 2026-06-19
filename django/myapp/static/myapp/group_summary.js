document.addEventListener("DOMContentLoaded", function () {
    const SUMMARY_API_URL = "/api/group_summary/";
    const PROMOTER_SEARCH_URL = "/query/";

    const tableBody = document.getElementById("summary-table-body");

    // get data from the db backend
    fetch(SUMMARY_API_URL)
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
        .then(data => {
            tableBody.innerHTML = "";

            if (!data.results || data.results.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="3" class="text-center">No group data found.</td></tr>`;
                return;
            }

            data.results.forEach(item => {
                const groupName = item.group ? item.group : "Unknown Group";
                const count = item.bacterium_count;

                const targetUrl = `${PROMOTER_SEARCH_URL}?group=${encodeURIComponent(groupName)}`;

                const row = document.createElement("tr");
                row.innerHTML = `
                    <td><strong>${groupName}</strong></td>
                    <td class="text-center">${count}</td>
                    <td class="text-center">
                        <a href="${targetUrl}" class="view-btn" title="View records for ${groupName}">
                            <i class="fa-solid fa-eye"></i>
                        </a>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => {
            console.error("Error fetching group summary:", error);
            tableBody.innerHTML = `<tr><td colspan="3" class="text-center" style="color: red;">Failed to load data. Please try again later.</td></tr>`;
        });
});