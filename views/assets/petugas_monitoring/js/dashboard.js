console.log("Stok Supabase Terbaca:", rawStok);

const validStok = rawStok.filter((s) => s.kaca && s.kaca.kategori);

const selKat = document.getElementById("kategori");
const selTeb = document.getElementById("ketebalan");
const selUk = document.getElementById("ukuran");
const output = document.getElementById("output");

const cats = [...new Set(validStok.map((s) => s.kaca.kategori.kategori))];
cats.forEach((c) => (selKat.innerHTML += `<option value="${c}">${c}</option>`));

function onKatChange() {
    const kat = selKat.value;
    selTeb.innerHTML = '<option value="">Pilih Ketebalan</option>';
    selUk.innerHTML = '<option value="">Pilih Ukuran</option>';
    selTeb.style.display = kat ? "block" : "none";
    selUk.style.display = "none";

    if (kat) {
        const tebals = [
            ...new Set(
                validStok
                    .filter((s) => s.kaca.kategori.kategori === kat)
                    .map((s) => s.kaca.ketebalan),
            ),
        ];
        tebals.forEach(
            (t) =>
                (selTeb.innerHTML += `<option value="${t}">${t} mm</option>`),
        );
    }
    renderOutput();
}

function onTebChange() {
    const kat = selKat.value;
    const teb = selTeb.value;
    selUk.innerHTML = '<option value="">Pilih Ukuran</option>';
    selUk.style.display = teb ? "block" : "none";

    if (teb) {
        const ukurans = [
            ...new Set(
                validStok
                    .filter(
                        (s) =>
                            s.kaca.kategori.kategori === kat &&
                            s.kaca.ketebalan === teb,
                    )
                    .map((s) => s.kaca.ukuran),
            ),
        ];
        ukurans.forEach(
            (u) => (selUk.innerHTML += `<option value="${u}">${u}</option>`),
        );
    }
    renderOutput();
}

function renderOutput() {
    const kat = selKat.value;
    const teb = selTeb.value;
    const uk = selUk.value;

    let filtered = validStok;
    if (kat)
        filtered = filtered.filter((s) => s.kaca.kategori.kategori === kat);
    if (teb) filtered = filtered.filter((s) => s.kaca.ketebalan === teb);
    if (uk) filtered = filtered.filter((s) => s.kaca.ukuran === uk);

    let agg = {};
    filtered.forEach((s) => {
        let label = `Kaca ${s.kaca.kategori.kategori}`;
        if (teb) label += ` (${s.kaca.ketebalan}mm)`;
        if (uk) label += ` - ${s.kaca.ukuran}`;

        if (!agg[label]) agg[label] = { baik: 0, rusak: 0 };
        if (s.kondisi === "Rusak" || s.kondisi === "rusak")
            agg[label].rusak += s.jumlah;
        else agg[label].baik += s.jumlah;
    });

    output.innerHTML = "";
    if (Object.keys(agg).length === 0) {
        output.innerHTML = "<div>Belum ada data stok kaca di Gudang.</div>";
        return;
    }

    for (let [label, vals] of Object.entries(agg)) {
        output.innerHTML += `<div>${label} : ${vals.baik}</div><div style="color: crimson;">${label} Rusak : ${vals.rusak}</div>`;
    }
}

document.addEventListener("DOMContentLoaded", renderOutput);

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
