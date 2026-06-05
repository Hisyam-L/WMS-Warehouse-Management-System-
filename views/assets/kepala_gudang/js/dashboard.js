const profileBtn = document.getElementById("profileBtn");
const profileDropdown = document.getElementById("profileDropdown");
if (profileBtn) {
    profileBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        profileDropdown.style.display =
            profileDropdown.style.display === "none" ? "block" : "none";
    });
}
window.addEventListener("click", (e) => {
    if (
        profileBtn &&
        profileDropdown &&
        !profileBtn.contains(e.target) &&
        !profileDropdown.contains(e.target)
    ) {
        profileDropdown.style.display = "none";
    }
});
const toggleBtn = document.getElementById("toggleBtn");
const sidebar = document.getElementById("sidebar");
if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
        sidebar.classList.toggle("close");
    });
}

let transactions = JSON.parse(
    document.getElementById("supabase-tx-data").getAttribute("data-json") ||
        "[]",
);

function renderTransactions(data) {
    const tbody = document.getElementById("transaksiBody");
    if (!tbody) return;
    tbody.innerHTML = "";
    if (data.length === 0) {
        tbody.innerHTML =
            '<tr><td colspan="8" class="text-center">Tidak ada transaksi</td></tr>';
        return;
    }
    data.forEach((trx) => {
        const row = tbody.insertRow();
        const statusClass =
            trx.status === "Masuk" ? "status-masuk" : "status-keluar";
        row.innerHTML = `
                    <td>${trx.tanggal}</td>
                    <td>${trx.waktu}</td>
                    <td><strong>${trx.jenis}</strong></td>
                    <td>${trx.ukuran}</td>
                    <td>${trx.ketebalan}</td>
                    <td><span class="status-badge ${statusClass}">${trx.status}</span></td>
                    <td>${trx.jumlah}</td>
                    <td><button class="btn-cek" data-id="${trx.id}">Cek Detail</button></td>
                `;
    });

    document.querySelectorAll(".btn-cek").forEach((btn) => {
        btn.addEventListener("click", (e) => {
            const id = parseInt(btn.getAttribute("data-id"));
            const found = transactions.find((t) => t.id === id);
            if (found) {
                alert(
                    `📄 Detail Transaksi\nJenis: ${found.jenis}\nUkuran: ${found.ukuran}\nKetebalan: ${found.ketebalan}\nStatus: ${found.status}\nJumlah: ${found.jumlah}\nHari: ${found.tanggal} ${found.waktu}`,
                );
            } else {
                alert("Transaksi tidak ditemukan");
            }
        });
    });
}

document
    .getElementById("inputTanggalFilter")
    ?.addEventListener("change", (e) => {
        let val = e.target.value;
        if (val) {
            let d = new Date(val);
            const months = [
                "Januari",
                "Februari",
                "Maret",
                "April",
                "Mei",
                "Juni",
                "Juli",
                "Agustus",
                "September",
                "Oktober",
                "November",
                "Desember",
            ];
            let indoDate = `${d.getDate()} ${months[d.getMonth()]} ${d.getFullYear()}`;

            const filtered = transactions.filter((t) => t.tanggal === indoDate);
            renderTransactions(filtered);
        } else {
            renderTransactions(transactions);
        }
    });

let stokData = JSON.parse(
    document.getElementById("supabase-stok-data").getAttribute("data-json") ||
        "[]",
);

function renderStok(data) {
    const container = document.querySelector(".stok-table-box");
    container.innerHTML = "";

    let grouped = {};
    data.forEach((item) => {
        if (!grouped[item.kategori])
            grouped[item.kategori] = { Baik: 0, Rusak: 0 };
        grouped[item.kategori][item.kondisi] += item.jumlah;
    });

    let html = "";
    for (let [kategori, detail] of Object.entries(grouped)) {
        html += `
        <div class="stok-row">
            <span class="stok-name">Kaca ${kategori}</span>
            <span class="stok-separator">:</span><span class="stok-number">${detail.Baik}</span>
        </div>
        <div class="stok-row">
            <span class="stok-name">${kategori} Rusak</span>
            <span class="stok-separator">:</span><span class="stok-number text-danger">${detail.Rusak}</span>
        </div>`;
    }

    if (Object.keys(grouped).length === 0) {
        html =
            '<div class="text-center text-muted py-3">Tidak ada data stok yang sesuai dengan filter.</div>';
    }
    container.innerHTML = html;
}

document
    .getElementById("filterUkuran")
    .addEventListener("change", applyStokFilter);
document
    .getElementById("filterKetebalan")
    .addEventListener("change", applyStokFilter);

function applyStokFilter() {
    let filterU = document.getElementById("filterUkuran").value;
    let filterK = document.getElementById("filterKetebalan").value;

    let filtered = stokData.filter((item) => {
        let matchU = filterU === "all" || item.ukuran.includes(filterU);
        let matchK = filterK === "all" || item.ketebalan.includes(filterK);
        return matchU && matchK;
    });
    renderStok(filtered);
}
renderStok(stokData);

function downloadCSV() {
    const headers = [
        "Tanggal",
        "Waktu",
        "Jenis Kaca",
        "Ukuran",
        "Ketebalan",
        "Status",
        "Jumlah",
    ];
    const rows = transactions.map((t) => [
        t.tanggal,
        t.waktu,
        t.jenis,
        t.ukuran,
        t.ketebalan,
        t.status,
        t.jumlah,
    ]);
    const csvContent = [headers, ...rows]
        .map((row) => row.join(","))
        .join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.href = url;
    link.setAttribute("download", "laporan_transaksi_gudang.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}
document
    .getElementById("btnDownloadCSV")
    ?.addEventListener("click", downloadCSV);

renderTransactions(transactions);
