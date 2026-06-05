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

const inviteCards = document.querySelectorAll(".invite-card");

inviteCards.forEach((card) => {
    card.addEventListener("click", async () => {
        const roleName = card.getAttribute("data-role");
        const konfirmasi = confirm(
            `Buat link undangan resmi untuk posisi ${roleName} ke WhatsApp?`,
        );
        if (!konfirmasi) return;

        const roleValue =
            roleName === "Petugas Monitor"
                ? "petugas_monitoring"
                : "petugas_pencatatan";

        let formData = new FormData();
        formData.append("role_tujuan", roleValue);

        try {
            let res = await fetch("/kepala_gudang/invite_api", {
                method: "POST",
                body: formData,
            });
            let data = await res.json();

            if (data.link) {
                let pesanText = `Halo! Silakan daftar sebagai *${roleName}* di WMS Gudang Kaca melalui link enkripsi berikut:\n\n${data.link}\n\n_Link berlaku selama 24 jam._`;
                let waUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent(pesanText)}`;
                window.open(waUrl, "_blank");
            }
        } catch (e) {
            alert("Gagal membuat link undangan.");
        }
    });
});

const acceptBtns = document.querySelectorAll(".accept-btn");
const rejectBtns = document.querySelectorAll(".reject-btn");

acceptBtns.forEach((btn) => {
    btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const row = btn.closest("tr");
        const username =
            row.querySelector("td:first-child")?.innerText?.trim() ||
            "Pengguna";
        btn.innerHTML = '<i class="bi bi-check-circle-fill"></i> accepted';
        btn.disabled = true;
        btn.style.background = "#e0f2e7";
        btn.style.color = "#166534";
        const siblingReject = row.querySelector(".reject-btn");
        if (siblingReject) {
            siblingReject.disabled = true;
            siblingReject.style.opacity = "0.5";
            siblingReject.style.cursor = "not-allowed";
        }
        alert(`✅ Akun "${username}" berhasil di-ACCEPT.`);
    });
});

rejectBtns.forEach((btn) => {
    btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const row = btn.closest("tr");
        const username =
            row.querySelector("td:first-child")?.innerText?.trim() ||
            "Pengguna";
        btn.innerHTML = '<i class="bi bi-x-circle-fill"></i> rejected';
        btn.disabled = true;
        btn.style.background = "#fee2e2";
        btn.style.color = "#b91c1c";
        const siblingAccept = row.querySelector(".accept-btn");
        if (siblingAccept) {
            siblingAccept.disabled = true;
            siblingAccept.style.opacity = "0.5";
            siblingAccept.style.cursor = "not-allowed";
        }
        alert(`❌ Akun "${username}" telah di-REJECT.`);
    });
});
