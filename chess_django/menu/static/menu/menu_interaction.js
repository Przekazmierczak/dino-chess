document.addEventListener('DOMContentLoaded', function () {
    let btn = document.querySelector('#btn');
    let sidebar = document.querySelector('#sidebar');
    
    function handleResize() {
        const viewportWidth = window.innerWidth;
    
        if (viewportWidth < 1300) {
            sidebar.classList.remove('active')
        } else {
            sidebar.classList.add('active')
        }
    };
    
    handleResize();
    window.addEventListener('resize', handleResize);
    
    btn.onclick = function () {
        sidebar.classList.toggle('active');
    };
    
    const toggleButton = document.getElementById('theme');
    const rootElement = document.documentElement;
    
    const currentTheme = localStorage.getItem('theme');
    if (currentTheme) {
        rootElement.classList.add(currentTheme);
    }
    
    toggleButton.addEventListener('click', () => {
        rootElement.classList.toggle('classic-mode');
    
        if (rootElement.classList.contains('classic-mode')) {
            localStorage.setItem('theme', 'classic-mode');
        } else {
            localStorage.removeItem('theme');
        }
    });
});