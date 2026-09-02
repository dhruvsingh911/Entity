document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.querySelector("form");
  const emailInput = document.querySelector('input[type="email"]');
  const continueButton = document.querySelector(
    'button[type="submit"]'
  );

  if (!continueButton) {
    console.error("Login button nahi mila.");
    return;
  }

  continueButton.addEventListener("click", (event) => {
    event.preventDefault();

    // Agar email field hai to check karega
    if (emailInput) {
      const email = emailInput.value.trim();

      if (email === "") {
        alert("Please enter your email.");
        emailInput.focus();
        return;
      }

      // Basic email validation
      if (!email.includes("@")) {
        alert("Please enter a valid email.");
        emailInput.focus();
        return;
      }
    }

    // Login successful → Index page
    window.location.href = "/index.html";
  });

  // Enter key se bhi login
  if (loginForm) {
    loginForm.addEventListener("submit", (event) => {
      event.preventDefault();

      continueButton.click();
    });
  }
});