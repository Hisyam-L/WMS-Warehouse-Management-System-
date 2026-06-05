let menuOpen = false;
function toggleMenu() {
    menuOpen = !menuOpen;
    document.getElementById("mobileMenu").style.display = menuOpen
        ? "flex"
        : "none";
}
function kirimPesan() {
    const input = document.getElementById("chatInput");
    const chatBox = document.getElementById("chatBox");
    const pesan = input.value.trim();
    if (pesan === "") return;
    const bubble = document.createElement("div");
    bubble.className = "bubble bubble-right";
    bubble.innerHTML = ` <div class="avatar"></div> <div class="message"> ${pesan} </div> `;
    chatBox.appendChild(bubble);
    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;
}
document.getElementById("chatInput").addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        kirimPesan();
    }
});
window.onload = function () {
    const chatBox = document.getElementById("chatBox");
    chatBox.scrollTop = chatBox.scrollHeight;
};
