const menuNavigasi = document.getElementById("menuNavigasi");

let menuOpen = false;

function toggleMenu() {
    if (window.innerWidth >= 768) {
        return;
    }

    menuOpen = !menuOpen;

    menuNavigasi.style.display = menuOpen ? "flex" : "none";
}
