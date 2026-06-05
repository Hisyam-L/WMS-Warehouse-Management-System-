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

const filterKondisi = document.getElementById("filterKondisi");
const filterUkuran = document.getElementById("filterUkuran");
const filterKetebalan = document.getElementById("filterKetebalan");
const glassCards = document.querySelectorAll(".glass-item");

function applyInstruksiFilter() {
    let valKon = filterKondisi ? filterKondisi.value : "all";
    let valU = filterUkuran ? filterUkuran.value : "all";
    let valK = filterKetebalan ? filterKetebalan.value : "all";

    glassCards.forEach((card) => {
        let kon = card.getAttribute("data-kondisi") || "Baik";
        let u = card.getAttribute("data-ukuran");
        let k = card.getAttribute("data-ketebalan");

        let matchKon =
            valKon === "all" || kon === valKon || (valKon === "all" && !kon);
        let matchU = valU === "all" || u === valU;
        let matchK = valK === "all" || k === valK;

        if (matchKon && matchU && matchK) {
            card.style.display = "flex";
        } else {
            card.style.display = "none";
        }
    });
}

if (filterKondisi)
    filterKondisi.addEventListener("change", applyInstruksiFilter);
if (filterUkuran) filterUkuran.addEventListener("change", applyInstruksiFilter);
if (filterKetebalan)
    filterKetebalan.addEventListener("change", applyInstruksiFilter);

const detailPanel = document.getElementById("detailPanel");
const namaKacaInput = document.getElementById("namaKaca");
const inputIdKaca = document.getElementById("inputIdKaca");

glassCards.forEach((card) => {
    card.addEventListener("click", () => {
        const id_kaca = card.getAttribute("data-id");
        const nama = card.getAttribute("data-nama");
        const kondisi = card.getAttribute("data-kondisi") || "Baik";

        namaKacaInput.value = nama + (kondisi === "Rusak" ? " (Rusak)" : "");
        inputIdKaca.value = id_kaca;
        detailPanel.classList.add("show");
    });
});

document.getElementById("closePanel").addEventListener("click", () => {
    detailPanel.classList.remove("show");
});
