let menuOpen = false;
function toggleMenu() {
    menuOpen = !menuOpen;
    const mobileMenu = document.getElementById("mobileMenu");
    mobileMenu.style.display = menuOpen ? "flex" : "none";
}
const imgInput = document.getElementById("imgInput");
const previewImage = document.getElementById("previewImage");
const uploadText = document.getElementById("uploadText");
function bukaKamera() {
    imgInput.click();
}
imgInput.addEventListener("change", function () {
    const file = this.files[0];
    if (!file) {
        return;
    }
    if (!file.type.startsWith("image/")) {
        alert("File harus berupa gambar");
        return;
    }
    const reader = new FileReader();
    reader.onload = function (event) {
        previewImage.src = vent.target.result;
        previewImage.style.display = "block";
        uploadText.style.display = "none";
    };
    reader.readAsDataURL(file);
});
