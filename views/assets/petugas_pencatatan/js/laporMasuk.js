document.addEventListener("DOMContentLoaded", function () {
    const daftarKaca = document.getElementById("daftarKaca");

    // 1. Render data kaca ke dalam Pop-up Modal
    if (typeof kacaData !== 'undefined' && kacaData.length > 0) {
        kacaData.forEach(k => {
            if (!k.kategori) return;

            let div = document.createElement("div");
            div.className = "kaca-item";
            div.innerHTML = `
                <div><b>${k.kategori.kategori}</b> <br> <small style="color: gray;">Ukuran: ${k.ukuran}</small></div>
                <div class="badge-tebal">${k.ketebalan} mm</div>
            `;

            // Pas salah satu baris diklik, isi otomatis kotak inputnya
            div.onclick = function() {
                document.getElementById("id_kaca").value = k.id_kaca;
                document.getElementById("kategori").value = k.kategori.kategori;
                document.getElementById("ukuran").value = k.ukuran;
                document.getElementById("ketebalan").value = k.ketebalan;
                tutupModal();
            };

            daftarKaca.appendChild(div);
        });
    } else {
        daftarKaca.innerHTML = "<p style='text-align:center; padding:15px; color: gray;'>Data di database kosong</p>";
    }

    // 2. Kalau user ngetik manual/ngedit setelah milih dari DB, ID otomatis di-reset
    ["kategori", "ukuran", "ketebalan"].forEach(id => {
        const el = document.getElementById(id);
        if(el) {
            el.addEventListener("input", function() {
                document.getElementById("id_kaca").value = "";
            });
        }
    });
});

// Fungsi Buka Tutup Modal
function bukaModal() { document.getElementById("modalKaca").style.display = "flex"; }
function tutupModal() { document.getElementById("modalKaca").style.display = "none"; }

// Fungsi fitur cari di dalam Modal
function filterKaca() {
    const search = document.getElementById("cariKaca").value.toLowerCase();
    const items = document.querySelectorAll(".kaca-item");
    items.forEach(item => {
        const text = item.innerText.toLowerCase();
        item.style.display = text.includes(search) ? "flex" : "none";
    });
}

// Tutup modal kalau klik di luar pop-up
window.addEventListener("click", function(event) {
    const modal = document.getElementById("modalKaca");
    if (event.target === modal) tutupModal();
});

// --- LOGIKA MENU / SIDEBAR ---
const profileBtn = document.getElementById("profileBtn");
const profileDropdown = document.getElementById("profileDropdown");
if (profileBtn) {
    profileBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        profileDropdown.style.display = profileDropdown.style.display === "none" ? "block" : "none";
    });
}
window.addEventListener("click", (e) => {
    if (profileBtn && profileDropdown && !profileBtn.contains(e.target) && !profileDropdown.contains(e.target)) {
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