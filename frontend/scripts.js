document.addEventListener("DOMContentLoaded", function() {
    const accordionItems = document.querySelectorAll(".accordion-item h3");
    
    accordionItems.forEach(item => {
        item.addEventListener("click", () => {
            const content = item.nextElementSibling;
            content.style.display = content.style.display === "block" ? "none" : "block";
        });
    });

    const form = document.querySelector("form");
    form.addEventListener("submit", function(event) {
        const name = document.getElementById("name").value;
        const email = document.getElementById("email").value;
        const message = document.getElementById("message").value;

        if (!name || !email || !message) {
            alert("All fields are required!");
            event.preventDefault(); // Prevent form submission
        } else if (!validateEmail(email)) {
            alert("Please enter a valid email address!");
            event.preventDefault();
        }
    });

    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    }
});
