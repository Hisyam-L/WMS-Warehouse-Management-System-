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

            div.onclick = function () {
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

    // 2. Kalau user ngetik manual, ID otomatis di-reset
    ["kategori", "ukuran", "ketebalan"].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener("input", function () {
                document.getElementById("id_kaca").value = "";
            });
        }
    });
});

// --- FUNGSI MODAL KACA DATABASE ---
function bukaModal() { document.getElementById("modalKaca").style.display = "flex"; }
function tutupModal() { document.getElementById("modalKaca").style.display = "none"; }

function filterKaca() {
    const search = document.getElementById("cariKaca").value.toLowerCase();
    const items = document.querySelectorAll(".kaca-item");
    items.forEach(item => {
        item.style.display = item.innerText.toLowerCase().includes(search) ? "flex" : "none";
    });
}

// Tutup modal kaca kalau klik di luar
window.addEventListener("click", function (event) {
    const modal = document.getElementById("modalKaca");
    if (event.target === modal) tutupModal();
});

// --- FUNGSI UPLOAD GAMBAR DARI FILE ---
const imgInput = document.getElementById("imgInput");
const previewImage = document.getElementById("previewImage");
const uploadText = document.getElementById("uploadText");

function bukaKamera() {
    imgInput.click();
}

imgInput.addEventListener("change", function () {
    const file = this.files[0];
    if (!file) return;
    if (!file.type.startsWith("image/")) {
        alert("File harus berupa gambar!");
        return;
    }
    const reader = new FileReader();
    reader.onload = function (e) {
        previewImage.src = e.target.result;
        previewImage.style.display = "block";
        uploadText.style.display = "none";
    };
    reader.readAsDataURL(file);
});

// --- LOGIKA MENU PROFIL ---
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

// --- LOGIKA SIDEBAR ---
const toggleBtn = document.getElementById("toggleBtn");
const sidebar = document.getElementById("sidebar");
if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
        sidebar.classList.toggle("close");
    });
}