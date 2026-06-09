const imgInput = document.getElementById("imgInput");
const previewImage = document.getElementById("previewImage");
const uploadText = document.getElementById("uploadText");
const gambarBase64Input = document.getElementById("gambar_base64");

function bukaKamera() {
    imgInput.click();
}

imgInput.addEventListener("change", function () {
    const file = this.files[0];
    if (!file) return;
    if (!file.type.startsWith("image/")) {
        alert("File harus berupa gambar");
        return;
    }
    const reader = new FileReader();
    reader.onload = function (event) {
        previewImage.src = event.target.result;
        previewImage.style.display = "block";
        uploadText.style.display = "none";
        gambarBase64Input.value = event.target.result;
    };
    reader.readAsDataURL(file);
});

// DROPDOWN DINAMIS
const selKat = document.getElementById("kategori");
const selUk = document.getElementById("ukuran");
const selTeb = document.getElementById("ketebalan");
const inputId = document.getElementById("id_kaca");
const inputJumlah = document.querySelector('input[name="jumlah_rusak"]');

// Isi dropdown kategori (hanya dari kacaData yang sudah difilter perusahaan di backend)
const categories = [
    ...new Set(
        kacaData.filter((k) => k.kategori).map((k) => k.kategori.kategori),
    ),
];
categories.forEach(
    (c) => (selKat.innerHTML += `<option value="${c}">${c}</option>`),
);

function loadUkuran() {
    const kat = selKat.value;
    selUk.innerHTML = '<option value="">Pilih Ukuran</option>';
    selTeb.innerHTML = '<option value="">Pilih Ketebalan</option>';
    inputId.value = "";

    // Reset jumlah rusak
    inputJumlah.max = "";
    inputJumlah.placeholder = "0";
    inputJumlah.value = "";

    const ukurans = [
        ...new Set(
            kacaData
                .filter((k) => k.kategori && k.kategori.kategori === kat)
                .map((k) => k.ukuran),
        ),
    ];
    ukurans.forEach(
        (u) => (selUk.innerHTML += `<option value="${u}">${u}</option>`),
    );
}

function loadKetebalan() {
    const kat = selKat.value;
    const uk = selUk.value;
    selTeb.innerHTML = '<option value="">Pilih Ketebalan</option>';
    inputId.value = "";

    // Reset jumlah rusak
    inputJumlah.max = "";
    inputJumlah.placeholder = "0";
    inputJumlah.value = "";

    const tebals = [
        ...new Set(
            kacaData
                .filter(
                    (k) =>
                        k.kategori &&
                        k.kategori.kategori === kat &&
                        k.ukuran === uk,
                )
                .map((k) => k.ketebalan),
        ),
    ];
    tebals.forEach(
        (t) => (selTeb.innerHTML += `<option value="${t}">${t} mm</option>`),
    );
}

function setIdKaca() {
    const kat = selKat.value;
    const uk = selUk.value;
    const tebal = selTeb.value;

    const kaca = kacaData.find(
        (k) =>
            k.kategori &&
            k.kategori.kategori === kat &&
            k.ukuran === uk &&
            k.ketebalan === tebal,
    );

    if (kaca) {
        inputId.value = kaca.id_kaca;

        // Set max jumlah rusak sesuai stok baik dari backend
        const stokBaik = kaca.stok_baik || 0;
        inputJumlah.max = stokBaik;
        inputJumlah.placeholder = `Maks ${stokBaik} pcs`;
        inputJumlah.value = "";
    } else {
        inputId.value = "";
        inputJumlah.max = "";
        inputJumlah.placeholder = "0";
        inputJumlah.value = "";
    }
}

// VALIDASI SEBELUM KIRIM
function validasiForm(event) {
    if (inputId.value === "") {
        event.preventDefault();
        alert(
            "Sistem tidak dapat mendeteksi ID Kaca. Harap pastikan Kategori, Ukuran, dan Ketebalan dipilih hingga selesai!",
        );
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
        alert(`Jumlah rusak tidak boleh melebihi stok baik saat ini (${max} pcs)!`);
        return;
    }
}

// --- LOGIKA MENU ---
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