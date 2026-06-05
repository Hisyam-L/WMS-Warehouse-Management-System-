document.addEventListener("DOMContentLoaded", function () {
    console.log("Data Kaca Supabase:", kacaData);

    const selKat = document.getElementById("kategori");
    const selUk = document.getElementById("ukuran");
    const selTeb = document.getElementById("ketebalan");
    const inputId = document.getElementById("id_kaca");

    if (!kacaData || kacaData.length === 0) {
        selKat.innerHTML =
            '<option value="">Data kaca di database kosong!</option>';
        return;
    }

    const categories = [
        ...new Set(
            kacaData
                .filter((k) => k.kategori)
                .map((k) => k.kategori.kategori),
        ),
    ];

    selKat.innerHTML =
        '<option value="">Pilih Kategori</option>';

    categories.forEach((c) => {
        selKat.innerHTML += `<option value="${c}">${c}</option>`;
    });

    window.loadUkuran = function () {
        const kat = selKat.value;

        selUk.innerHTML =
            '<option value="">Pilih Ukuran</option>';

        selTeb.innerHTML =
            '<option value="">Pilih Ketebalan</option>';

        inputId.value = "";

        if (!kat) return;

        const ukurans = [
            ...new Set(
                kacaData
                    .filter(
                        (k) =>
                            k.kategori &&
                            k.kategori.kategori === kat,
                    )
                    .map((k) => k.ukuran),
            ),
        ];

        ukurans.forEach((u) => {
            selUk.innerHTML += `<option value="${u}">${u}</option>`;
        });
    };

    window.loadKetebalan = function () {
        const kat = selKat.value;
        const uk = selUk.value;

        selTeb.innerHTML =
            '<option value="">Pilih Ketebalan</option>';

        inputId.value = "";

        if (!kat || !uk) return;

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

        tebals.forEach((t) => {
            selTeb.innerHTML += `<option value="${t}">${t} mm</option>`;
        });
    };

    window.setIdKaca = function () {
        const kat = selKat.value;
        const uk = selUk.value;
        const tebal = selTeb.value.replace(" mm", "");

        const kaca = kacaData.find(
            (k) =>
                k.kategori &&
                k.kategori.kategori === kat &&
                k.ukuran === uk &&
                k.ketebalan === tebal,
        );

        inputId.value = kaca ? kaca.id_kaca : "";
    };

    window.validasiForm = function (event) {
        if (inputId.value === "") {
            event.preventDefault();
            alert(
                "Harap pilih Kategori, Ukuran, dan Ketebalan kaca hingga selesai!",
            );
        }
    };
});

const profileBtn = document.getElementById("profileBtn");
const profileDropdown =
    document.getElementById("profileDropdown");

if (profileBtn) {
    profileBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        profileDropdown.style.display =
            profileDropdown.style.display === "none"
                ? "block"
                : "none";
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