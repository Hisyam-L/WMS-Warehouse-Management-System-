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
        // Tampilkan Preview
        previewImage.src = event.target.result;
        previewImage.style.display = "block";
        uploadText.style.display = "none";

        // Masukkan Hasil Gambar Base64 ke Input Hidden Form
        gambarBase64Input.value = event.target.result;
    };
    reader.readAsDataURL(file);
});

// DROPDOWN DINAMIS
const selKat = document.getElementById("kategori");
const selUk = document.getElementById("ukuran");
const selTeb = document.getElementById("ketebalan");
const inputId = document.getElementById("id_kaca");

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
    } else {
        inputId.value = "";
    }
}

// VALIDASI SEBELUM KIRIM
function validasiForm(event) {
    if (inputId.value === "") {
        event.preventDefault(); // Cegah form terkirim
        alert(
            "Sistem tidak dapat mendeteksi ID Kaca. Harap pastikan Kategori, Ukuran, dan Ketebalan dipilih hingga selesai!",
        );
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
