// --- LOGIKA NAVBAR & SIDEBAR ---
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

// --- LOGIKA CHAT ---
let currentLawanId = null;
let lastPesanCount = 0;

function pilihChat(id_lawan, nama_lawan, element) {
    currentLawanId = id_lawan;
    lastPesanCount = 0; // Reset counter saat ganti kontak

    document.getElementById("chatTitle").innerText = nama_lawan;
    document.getElementById("inputArea").style.display = "block";

    document.querySelectorAll(".user-card").forEach((el) => el.classList.remove("active"));
    if (element) element.classList.add("active");

    loadPesan();
}

async function loadPesan() {
    if (!currentLawanId) return;
    try {
        const res = await fetch(`/petugas_pencatatan/api/pesan?lawan_id=${currentLawanId}`);
        const data = await res.json();
        const container = document.getElementById("chatContainer");

        // Hanya render ulang kalau jumlah pesan berubah
        if (data.pesan.length === lastPesanCount) return;
        lastPesanCount = data.pesan.length;

        // Cek posisi scroll sebelum render ulang
        const isAtBottom = container.scrollHeight - container.scrollTop <= container.clientHeight + 100;

        if (data.pesan.length === 0) {
            container.innerHTML = `<div style="text-align: center; color: #9ca3af; margin-top: 50px;">Belum ada percakapan dengan pengguna ini</div>`;
            return;
        }

        container.innerHTML = "";
        data.pesan.forEach((p) => {
            const isMe = p.id_pengirim === data.my_id;
            const time = new Date(p.waktu).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            container.innerHTML += `
                <div class="chat-row ${isMe ? 'right' : 'left'}">
                    ${!isMe ? '<div class="chat-avatar"><i class="bi bi-person-fill"></i></div>' : ""}
                    <div class="chat-bubble ${isMe ? 'chat-right' : 'chat-left'}">
                        <div style="font-size: 14px;">${p.isi}</div>
                        <div style="font-size: 10px; text-align: ${isMe ? 'right' : 'left'}; margin-top: 5px; opacity: 0.7;">${time}</div>
                    </div>
                    ${isMe ? '<div class="chat-avatar"><i class="bi bi-person-fill"></i></div>' : ""}
                </div>
            `;
        });

        // Auto scroll ke bawah hanya kalau user sudah di bawah
        if (isAtBottom) {
            container.scrollTop = container.scrollHeight;
        }

    } catch (err) {
        console.error("Gagal load pesan:", err);
    }
}

// Interval refresh tiap 2 detik
setInterval(loadPesan, 2000);

async function sendMessage() {
    const input = document.getElementById("messageInput");
    if (input.value.trim() === "" || !currentLawanId) return;

    try {
        await fetch("/petugas_pencatatan/api/pesan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                id_penerima: currentLawanId,
                isi: input.value,
            }),
        });

        input.value = "";
        lastPesanCount = 0; // Force render ulang setelah kirim pesan sendiri
        await loadPesan();

        // Paksa scroll ke bawah setelah kirim
        const container = document.getElementById("chatContainer");
        setTimeout(() => (container.scrollTop = container.scrollHeight), 100);

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