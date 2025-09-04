document.addEventListener("DOMContentLoaded", () => {
  // Botón copiar enlace corto
  const btnCopy = document.getElementById("btn-copy");
  const shortUrl = document.getElementById("short-url");
  const messageBox = document.getElementById("message");

  if (btnCopy && shortUrl) {
    btnCopy.addEventListener("click", () => {
      navigator.clipboard.writeText(shortUrl.textContent.trim())
        .then(() => showMessage("¡Enlace copiado con éxito!", "success"))
        .catch(() => showMessage("Error al copiar el enlace.", "error"));
    });
  }

  // Botón copiar email
  const btnCopyEmail = document.getElementById("btn-copy-email");
  const userEmail = document.getElementById("user-email");
  if (btnCopyEmail && userEmail) {
    btnCopyEmail.addEventListener("click", () => {
      navigator.clipboard.writeText(userEmail.textContent.trim())
        .then(() => showMessage("¡Correo copiado con éxito!", "success"))
        .catch(() => showMessage("Error al copiar el correo.", "error"));
    });
  }

  // Botón enviar email (solo abre cliente mailto, sin copiar)
  const btnSendEmail = document.getElementById("btn-send-email");
  if (btnSendEmail) {
    btnSendEmail.addEventListener("click", () => {
      const email = userEmail.textContent.trim();
      window.location.href = `mailto:${email}`;
    });
  }

  function showMessage(text, type) {
    messageBox.textContent = text;
    messageBox.className = `message ${type}`;
    setTimeout(() => {
      messageBox.textContent = "";
      messageBox.className = "message";
    }, 3000);
  }
});
