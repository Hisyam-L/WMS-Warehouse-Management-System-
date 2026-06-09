// --- LOGIKA MENU / SIDEBAR ---

document.addEventListener("DOMContentLoaded", function () {
  // --- 1. LOGIKA TAB (AKAN DIBELI & SUDAH DIBELI) ---
  const btnAkan = document.getElementById('tabAkanDibeli');
  const btnSudah = document.getElementById('tabSudahDibeli');
  const daftarAkan = document.getElementById('daftarAkanDibeli');
  const daftarSudah = document.getElementById('daftarSudahDibeli');

  if (btnAkan && btnSudah) {
    btnAkan.addEventListener('click', function () {
      btnAkan.classList.add('aktif');
      btnSudah.classList.remove('aktif');
      daftarAkan.classList.add('tampilkan');
      daftarSudah.classList.remove('tampilkan');
    });

    btnSudah.addEventListener('click', function () {
      btnSudah.classList.add('aktif');
      btnAkan.classList.remove('aktif');
      daftarSudah.classList.add('tampilkan');
      daftarAkan.classList.remove('tampilkan');
    });
  }

  // --- 2. LOGIKA SIDEBAR & DROPDOWN ---
  const profileBtn = document.getElementById("profileBtn");
  const profileDropdown = document.getElementById("profileDropdown");

  if (profileBtn) {
    profileBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      // Fix: fallback ke "none" kalau inline style belum pernah di-set
      const isVisible = (profileDropdown.style.display || "none") === "block";
      profileDropdown.style.display = isVisible ? "none" : "block";
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
});