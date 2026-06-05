let menuOpen = false;

function toggleMenu() {
    if (window.innerWidth >= 768) {
        return;
    }

    const mobileMenu = document.getElementById("mobileMenu");

    menuOpen = !menuOpen;

    mobileMenu.style.display = menuOpen ? "flex" : "none";
}
