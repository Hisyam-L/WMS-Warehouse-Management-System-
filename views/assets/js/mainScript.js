const toggleBtn = document.getElementById("toggleBtn");
const sidebar = document.getElementById("sidebar");
const icon = toggleBtn.querySelector("i");

toggleBtn.addEventListener("click", () => {
    sidebar.classList.toggle("close");
    if (sidebar.classList.contains("close")) {
        icon.classList.replace("bi-x", "bi-list");
    } else {
        icon.classList.replace("bi-list", "bi-x");
    }
});
