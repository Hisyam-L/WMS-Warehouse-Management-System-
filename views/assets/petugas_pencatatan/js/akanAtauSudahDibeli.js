let menuOpen = false;

        function toggleMenu() {

            if (window.innerWidth >= 768) {
                return;
            }

            menuOpen = !menuOpen;

            const mobileMenu =
                document.getElementById("menuMobile");

            mobileMenu.style.display =
                menuOpen ? "flex" : "none";
        }

        const tombolAkanDibeli =
            document.getElementById(
                'tabAkanDibeli'
            );

        const tombolSudahDibeli =
            document.getElementById(
                'tabSudahDibeli'
            );

        const daftarAkanDibeli =
            document.getElementById(
                'daftarAkanDibeli'
            );

        const daftarSudahDibeli =
            document.getElementById(
                'daftarSudahDibeli'
            );

        tombolAkanDibeli.addEventListener(
            'click',
            function () {

                tombolAkanDibeli.classList.remove(
                    'tidakAktif'
                );

                tombolAkanDibeli.classList.add(
                    'aktif'
                );

                tombolSudahDibeli.classList.remove(
                    'aktif'
                );

                tombolSudahDibeli.classList.add(
                    'tidakAktif'
                );

                daftarAkanDibeli.classList.add(
                    'tampilkan'
                );

                daftarSudahDibeli.classList.remove(
                    'tampilkan'
                );
            }
        );

        tombolSudahDibeli.addEventListener(
            'click',
            function () {

                tombolSudahDibeli.classList.remove(
                    'tidakAktif'
                );

                tombolSudahDibeli.classList.add(
                    'aktif'
                );

                tombolAkanDibeli.classList.remove(
                    'aktif'
                );

                tombolAkanDibeli.classList.add(
                    'tidakAktif'
                );

                daftarSudahDibeli.classList.add(
                    'tampilkan'
                );

                daftarAkanDibeli.classList.remove(
                    'tampilkan'
                );
            }
        );