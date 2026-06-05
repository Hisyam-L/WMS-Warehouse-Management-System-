let menuOpen = false;

function toggleMenu() {
    menuOpen = !menuOpen;

    document.getElementById("mobileMenu").style.display = menuOpen
        ? "flex"
        : "none";
}
