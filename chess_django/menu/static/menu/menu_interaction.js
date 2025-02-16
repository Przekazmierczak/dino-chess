document.addEventListener('DOMContentLoaded', function () {
    let btn = document.querySelector('#btn');
    let sidebar = document.querySelector('#sidebar');
    
    // Function to handle window resizing and toggle sidebar visibility
    function handleResize() {
        const viewportWidth = window.innerWidth;  // Get the current width of the viewport
        
        // If the viewport width is less than 1300px, remove 'active' class from sidebar to hide it
        if (viewportWidth < 1500) {
            sidebar.classList.remove('active')
        } else {
            // If the viewport is wider, add the 'active' class to show the sidebar
            sidebar.classList.add('active')
        }
    };
    
    // Call handleResize function to set the initial state based on the current viewport size
    handleResize();
    // Add an event listener for window resize to dynamically adjust sidebar visibility
    window.addEventListener('resize', handleResize);
    
    // Set up an event listener on the button to toggle the 'active' class on the sidebar
    btn.onclick = function () {
        sidebar.classList.toggle('active');
    };
    
    const toggleButton = document.getElementById('theme');
    const rootElement = document.documentElement;
    
    // Check local storage for a saved theme preference and apply it if it exists
    const currentTheme = localStorage.getItem('theme');
    if (currentTheme) {
        rootElement.classList.add(currentTheme);
    }
    
    // Add an event listener to the theme toggle button to switch between themes
    toggleButton.addEventListener('click', () => {
        // Toggle the 'classic-mode' class on the root element
        rootElement.classList.toggle('classic-mode');
        
        // If 'classic-mode' is now active, save it in local storage, otherwise remove it
        if (rootElement.classList.contains('classic-mode')) {
            localStorage.setItem('theme', 'classic-mode');
        } else {
            localStorage.removeItem('theme');
        }
    });
});