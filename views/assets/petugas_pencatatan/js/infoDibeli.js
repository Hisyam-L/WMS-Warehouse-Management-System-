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