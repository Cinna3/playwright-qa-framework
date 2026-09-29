document.getElementById("toggle-button").addEventListener("click", () => {
  const details = document.getElementById("details");
  details.hidden = !details.hidden;
});

document.getElementById("signup-form").addEventListener("submit", (event) => {
  event.preventDefault();

  const email = document.getElementById("email").value.trim();
  const error = document.getElementById("email-error");
  const success = document.getElementById("signup-success");

  error.hidden = true;
  success.hidden = true;

  const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  if (!isValid) {
    error.hidden = false;
    return;
  }

  success.hidden = false;
});
