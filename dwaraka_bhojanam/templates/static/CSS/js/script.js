// Example: Scroll to top on load
window.onload = () => {
    window.scrollTo(0, 0);
};


function toggleForm(formType) {
    const loginForm = document.getElementById("loginForm");
    const signupForm = document.getElementById("signupForm");
    const loginBtn = document.getElementById("loginBtn");
    const signupBtn = document.getElementById("signupBtn");

    if (formType === "login") {
        loginForm.style.display = "flex";
        signupForm.style.display = "none";
        loginBtn.classList.add("active");
        signupBtn.classList.remove("active");
    } else {
        loginForm.style.display = "none";
        signupForm.style.display = "flex";
        signupBtn.classList.add("active");
        loginBtn.classList.remove("active");
    }
}
