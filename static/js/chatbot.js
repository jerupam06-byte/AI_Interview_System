/**
 * AI Interview Assistant Chat Controller
 */

document.addEventListener("DOMContentLoaded", () => {
  const chatForm = document.getElementById("chat-form");
  const chatInput = document.getElementById("chat-input");
  const messagesContainer = document.getElementById("chat-messages");
  const sendBtn = document.getElementById("chat-send-btn");

  if (!chatForm || !chatInput || !messagesContainer) return;

  function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function appendMessage(text, sender) {
    const bubble = document.createElement("div");
    bubble.className = `chat-bubble ${sender}`;

    // Simple markdown parsing for bold and backticks
    let formattedText = text
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.*?)\*/g, "<em>$1</em>")
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\n/g, "<br>");

    bubble.innerHTML = formattedText;
    messagesContainer.appendChild(bubble);
    scrollToBottom();
    return bubble;
  }

  function appendTypingIndicator() {
    const bubble = document.createElement("div");
    bubble.className = "chat-bubble assistant typing-indicator";
    bubble.id = "typing-bubble";
    bubble.innerHTML = `<em>Assistant is thinking...</em>`;
    messagesContainer.appendChild(bubble);
    scrollToBottom();
  }

  function removeTypingIndicator() {
    const bubble = document.getElementById("typing-bubble");
    if (bubble) bubble.remove();
  }

  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const msg = chatInput.value.trim();
    if (!msg) return;

    // Append user message
    appendMessage(msg, "user");
    chatInput.value = "";
    chatInput.disabled = true;
    sendBtn.disabled = true;

    // Show indicator
    appendTypingIndicator();

    try {
      const response = await fetch("/assistant/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest"
        },
        body: JSON.stringify({ message: msg })
      });

      removeTypingIndicator();

      if (!response.ok) {
        throw new Error(`Server returned error ${response.status}`);
      }

      const data = await response.json();
      appendMessage(data.reply, "assistant");
    } catch (err) {
      removeTypingIndicator();
      appendMessage(`Sorry, an error occurred while connecting to the assistant: ${err.message}. Please try again.`, "assistant");
    } finally {
      chatInput.disabled = false;
      sendBtn.disabled = false;
      chatInput.focus();
    }
  });

  scrollToBottom();
});
