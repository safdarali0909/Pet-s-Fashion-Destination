document.addEventListener('DOMContentLoaded', function() {
    const searchBar = document.getElementById('search-bar');
    const searchToggle = document.getElementById('search-toggle');
    const menuToggle = document.getElementById('menu-toggle');
    const navLinks = document.querySelector('.nav-links');

    searchToggle.addEventListener('click', function() {
        searchBar.classList.toggle('open');
    });

    menuToggle.addEventListener('click', function() {
        navLinks.classList.toggle('mobile');
        navLinks.classList.toggle('show');
    });
});

