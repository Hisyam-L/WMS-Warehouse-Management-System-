// ========================================================
// CONFIG SUPABASE (dibaca dari meta tag di HTML)
// ========================================================
const SUPABASE_URL = document.querySelector('meta[name="supabase-url"]').content;
const SUPABASE_KEY = document.querySelector('meta[name="supabase-key"]').content;

// ========================================================
// UPLOAD GAMBAR KE SUPABASE STORAGE (bucket: laporan-images)
// ========================================================
const imgInput        = document.getElementById("imgInput");
const previewImage    = document.getElementById("previewImage");
const uploadText      = document.getElementById("uploadText");
const uploadBox       = document.querySelector(".upload-box");
const gambarUrlInput  = document.getElementById("gambar_url");

function bukaKamera() { imgInput.click(); }

imgInput.addEventListener("change", async function () {
    const file = this.files[0];
    if (!file) return;
    if (!file.type.startsWith("image/")) {
        alert("File harus berupa gambar!");
        return;
    }

    // Preview lokal dulu
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        previewImage.style.display = "block";
        uploadText.style.display = "none";
    };
    reader.readAsDataURL(file);

    // Loading indicator
    uploadBox.classList.add("uploading");
    uploadText.textContent = "Mengupload...";
    uploadText.style.display = "block";
    previewImage.style.display = "none";

    try {
        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch("/petugas_monitoring/api/upload_gambar", {
            method: "POST",
            body: formData
        });

        const data = await res.json();
        if (!res.ok || data.error) {
            throw new Error(data.error || "Upload gagal");
        }

        const publicUrl = data.url;
        gambarUrlInput.value = publicUrl;

        previewImage.src = publicUrl;
        previewImage.style.display = "block";
        uploadText.style.display = "none";
        uploadBox.classList.remove("uploading");
        uploadBox.classList.add("uploaded");

    } catch (err) {
        console.error("Upload error:", err);
        alert("Gagal upload foto: " + err.message);
        uploadText.textContent = "Klik untuk buka kamera";
        uploadText.style.display = "block";
        previewImage.style.display = "none";
        uploadBox.classList.remove("uploading");
        gambarUrlInput.value = "";
        imgInput.value = "";
    }
});

// ========================================================
// DROPDOWN DINAMIS (Kategori → Ukuran → Ketebalan)
// ========================================================
const selKat     = document.getElementById("kategori");
const selUk      = document.getElementById("ukuran");
const selTeb     = document.getElementById("ketebalan");
const inputId    = document.getElementById("id_kaca");
const inputJumlah = document.querySelector('input[name="jumlah_rusak"]');

const categories = [...new Set(kacaData.filter(k => k.kategori).map(k => k.kategori.kategori))];
categories.forEach(c => (selKat.innerHTML += `<option value="${c}">${c}</option>`));

function loadUkuran() {
    const kat = selKat.value;
    selUk.innerHTML = '<option value="">Pilih Ukuran</option>';
    selTeb.innerHTML = '<option value="">Pilih Ketebalan</option>';
    inputId.value = "";
    resetJumlah();

    const ukurans = [...new Set(kacaData.filter(k => k.kategori && k.kategori.kategori === kat).map(k => k.ukuran))];
    ukurans.forEach(u => (selUk.innerHTML += `<option value="${u}">${u}</option>`));
}

function loadKetebalan() {
    const kat = selKat.value;
    const uk  = selUk.value;
    selTeb.innerHTML = '<option value="">Pilih Ketebalan</option>';
    inputId.value = "";
    resetJumlah();

    const tebals = [...new Set(kacaData.filter(k => k.kategori && k.kategori.kategori === kat && k.ukuran === uk).map(k => k.ketebalan))];
    tebals.forEach(t => (selTeb.innerHTML += `<option value="${t}">${t} mm</option>`));
}

function setIdKaca() {
    const kat   = selKat.value;
    const uk    = selUk.value;
    const tebal = selTeb.value;

    const kaca = kacaData.find(k =>
        k.kategori && k.kategori.kategori === kat && k.ukuran === uk && k.ketebalan === tebal
    );

    if (kaca) {
        inputId.value = kaca.id_kaca;
        const stokBaik = kaca.stok_baik || 0;
        inputJumlah.max = stokBaik;
        inputJumlah.placeholder = `Maks ${stokBaik} pcs`;
        inputJumlah.value = "";

        // Tampilkan foto kaca (akan diganti foto rusak saat dilaporkan)
        if (kaca.gambar && !gambarUrlInput.value) {
            previewImage.src = kaca.gambar;
            previewImage.style.display = "block";
            uploadText.style.display = "none";
        }
    } else {
        inputId.value = "";
        resetJumlah();
    }
}

function resetJumlah() {
    inputJumlah.max = "";
    inputJumlah.placeholder = "0";
    inputJumlah.value = "";
}

// ========================================================
// VALIDASI FORM
// ========================================================
function validasiForm(event) {
    if (!inputId.value) {
        event.preventDefault();
        alert("Pilih kaca terlebih dahulu (Kategori → Ukuran → Ketebalan)!");
        return;
    }
    const val = parseInt(inputJumlah.value);
    const max = parseInt(inputJumlah.max);
    if (!val || val < 1) {
        event.preventDefault();
        alert("Jumlah rusak minimal 1 pcs!");
        return;
    }
    if (max && val > max) {
        event.preventDefault();
        alert(`Jumlah rusak tidak boleh melebihi stok baik (${max} pcs)!`);
        return;
    }
}

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
const sidebar   = document.getElementById("sidebar");
if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
        sidebar.classList.toggle("close");
    });
}