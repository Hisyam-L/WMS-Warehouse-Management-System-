// ========================================================
// CONFIG SUPABASE (dibaca dari meta tag di HTML)
// ========================================================
const SUPABASE_URL = document.querySelector('meta[name="supabase-url"]').content;
const SUPABASE_KEY = document.querySelector('meta[name="supabase-key"]').content;

// ========================================================
// UPLOAD GAMBAR KE SUPABASE STORAGE
// ========================================================
const imgInput    = document.getElementById("imgInput");
const previewImage = document.getElementById("previewImage");
const uploadText  = document.getElementById("uploadText");
const uploadBox   = document.querySelector(".boxUpload");
const gambarUrlInput = document.getElementById("gambar_url");

function bukaKamera() { imgInput.click(); }

imgInput.addEventListener("change", async function () {
    const file = this.files[0];
    if (!file) return;
    if (!file.type.startsWith("image/")) {
        alert("File harus berupa gambar!");
        return;
    }

    // Tampil preview lokal dulu
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        previewImage.style.display = "block";
        uploadText.style.display = "none";
    };
    reader.readAsDataURL(file);

    // Tampilkan indikator loading
    uploadBox.classList.add("uploading");
    uploadText.textContent = "Mengupload...";
    uploadText.style.display = "block";
    previewImage.style.display = "none";

    try {
        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch("/petugas_pencatatan/api/upload_gambar", {
            method: "POST",
            body: formData
        });

        const data = await res.json();
        if (!res.ok || data.error) {
            throw new Error(data.error || "Upload gagal");
        }

        const publicUrl = data.url;
        gambarUrlInput.value = publicUrl;

        // Tampilkan preview dari URL
        previewImage.src = publicUrl;
        previewImage.style.display = "block";
        uploadText.style.display = "none";
        uploadBox.classList.remove("uploading");
        uploadBox.classList.add("uploaded");

    } catch (err) {
        console.error("Upload error:", err);
        alert("Gagal upload gambar: " + err.message);
        uploadText.textContent = "Klik untuk buka kamera / galeri";
        uploadText.style.display = "block";
        previewImage.style.display = "none";
        uploadBox.classList.remove("uploading");
        gambarUrlInput.value = "";
        imgInput.value = "";
    }
});

// ========================================================
// MODAL KACA DATABASE
// ========================================================
document.addEventListener("DOMContentLoaded", function () {
    const daftarKaca = document.getElementById("daftarKaca");

    if (typeof kacaData !== 'undefined' && kacaData.length > 0) {
        kacaData.forEach(k => {
            if (!k.kategori) return;
            let div = document.createElement("div");
            div.className = "kaca-item";
            div.innerHTML = `
                <div>
                    <b>${k.kategori.kategori}</b>
                    ${k.gambar ? `<img src="${k.gambar}" style="width:36px;height:36px;object-fit:cover;border-radius:6px;margin-left:8px;vertical-align:middle;">` : ''}
                    <br><small style="color: gray;">Ukuran: ${k.ukuran}</small>
                </div>
                <div class="badge-tebal">${k.ketebalan} mm</div>
            `;
            div.onclick = function () {
                document.getElementById("id_kaca").value = k.id_kaca;
                document.getElementById("kategori").value = k.kategori.kategori;
                document.getElementById("ukuran").value = k.ukuran;
                document.getElementById("ketebalan").value = k.ketebalan;

                // Tampilkan gambar kaca yang sudah ada (jika ada)
                if (k.gambar) {
                    previewImage.src = k.gambar;
                    previewImage.style.display = "block";
                    uploadText.style.display = "none";
                    gambarUrlInput.value = k.gambar;
                }
                tutupModal();
            };
            daftarKaca.appendChild(div);
        });
    } else {
        daftarKaca.innerHTML = "<p style='text-align:center; padding:15px; color: gray;'>Data di database kosong</p>";
    }

    // Reset ID kaca kalau user ngetik manual
    ["kategori", "ukuran", "ketebalan"].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener("input", function () {
                document.getElementById("id_kaca").value = "";
            });
        }
    });
});

function bukaModal() { document.getElementById("modalKaca").style.display = "flex"; }
function tutupModal() { document.getElementById("modalKaca").style.display = "none"; }

function filterKaca() {
    const search = document.getElementById("cariKaca").value.toLowerCase();
    const items = document.querySelectorAll(".kaca-item");
    items.forEach(item => {
        item.style.display = item.innerText.toLowerCase().includes(search) ? "flex" : "none";
    });
}

window.addEventListener("click", function (event) {
    const modal = document.getElementById("modalKaca");
    if (event.target === modal) tutupModal();
});

// ========================================================
// PROFIL DROPDOWN
// ========================================================
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
    if (profileBtn && profileDropdown &&
        !profileBtn.contains(e.target) && !profileDropdown.contains(e.target)) {
        profileDropdown.style.display = "none";
    }
});

// ========================================================
// SIDEBAR TOGGLE (Desktop)
// ========================================================
const toggleBtn = document.getElementById("toggleBtn");
const sidebar = document.getElementById("sidebar");
if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
        sidebar.classList.toggle("close");
    });
}