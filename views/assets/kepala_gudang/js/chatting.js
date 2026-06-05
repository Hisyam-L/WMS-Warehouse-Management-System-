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

let currentLawanId = null;

async function pilihChat(id_lawan, nama_lawan, element) {
    currentLawanId = id_lawan;
    document.getElementById("chatTitle").innerText = "Chat - " + nama_lawan;
    document.getElementById("inputArea").style.display = "block";

    document
        .querySelectorAll(".user-card")
        .forEach((el) => el.classList.remove("active"));
    if (element) element.classList.add("active");

    loadPesan();
}

async function loadPesan() {
    if (!currentLawanId) return;
    try {
        let res = await fetch(
            `/kepala_gudang/api/pesan?lawan_id=${currentLawanId}`,
        );
        let data = await res.json();

        const container = document.getElementById("chatContainer");
        container.innerHTML = "";

        data.pesan.forEach((p) => {
            let isMe = p.id_pengirim === data.my_id;
            container.innerHTML += `
                        <div class="chat-row ${isMe ? "right" : ""}">
                            ${!isMe ? '<div class="chat-avatar"></div>' : ""}
                            <div class="chat-bubble ${isMe ? "chat-right" : "chat-left"}">${p.isi}</div>
                            ${isMe ? '<div class="chat-avatar"></div>' : ""}
                        </div>
                    `;
        });
        container.scrollTop = container.scrollHeight;
    } catch (err) {
        console.error("Gagal load pesan:", err);
    }
}

setInterval(loadPesan, 2000);

async function sendMessage() {
    const input = document.getElementById("messageInput");
    if (input.value.trim() === "" || !currentLawanId) return;

    try {
        await fetch("/kepala_gudang/api/pesan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                id_penerima: currentLawanId,
                isi: input.value,
            }),
        });
        input.value = "";
        loadPesan();
    } catch (err) {
        console.error("Gagal kirim pesan:", err);
    }
}

document.getElementById("sendBtn").addEventListener("click", sendMessage);
document.getElementById("messageInput").addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        sendMessage();
    }
});
