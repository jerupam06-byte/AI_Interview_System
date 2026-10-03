/**
 * Interview Controller
 * Manages timer for Real Mode, draft autosave, word counters, and submission.
 */

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("answer-form");
  const textarea = document.getElementById("answer-input");
  const wordCountDisplay = document.getElementById("word-count");
  const timerBadge = document.getElementById("timer-badge");
  const timerText = document.getElementById("timer-text");

  const interviewId = form ? form.dataset.interviewId : null;
  const questionId = form ? form.dataset.questionId : null;
  const isRealMode = form ? form.dataset.realMode === "true" : false;

  // 1. Initialize Voice Controller
  if (window.VoiceInputController) {
    new window.VoiceInputController({
      buttonId: "voice-btn",
      targetInputId: "answer-input",
      statusId: "voice-status"
    });
  }

  // 2. Draft Autosave & Word Count
  const draftKey = `draft_interview_${interviewId}_q_${questionId}`;

  function updateWordCount() {
    if (!textarea || !wordCountDisplay) return;
    const text = textarea.value.trim();
    const count = text ? text.split(/\s+/).length : 0;
    wordCountDisplay.textContent = `${count} word${count === 1 ? "" : "s"}`;
  }

  if (textarea) {
    // Restore draft if exists
    const savedDraft = sessionStorage.getItem(draftKey);
    if (savedDraft && !textarea.value) {
      textarea.value = savedDraft;
    }
    updateWordCount();

    textarea.addEventListener("input", () => {
      sessionStorage.setItem(draftKey, textarea.value);
      updateWordCount();
    });

    // Submit on Ctrl+Enter or Cmd+Enter
    textarea.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        if (form) form.submit();
      }
    });
  }

  // 3. Clear draft on form submission
  if (form) {
    form.addEventListener("submit", () => {
      sessionStorage.removeItem(draftKey);
      const submitBtn = document.getElementById("submit-btn");
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span>Evaluating Answer...</span>`;
      }
    });
  }

  // 4. Timer for Real Interview Mode
  if (isRealMode && timerBadge && timerText) {
    let timeLeft = parseInt(form.dataset.timeLimit || "120", 10); // 120 seconds default

    function formatTime(seconds) {
      const mins = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
    }

    timerText.textContent = formatTime(timeLeft);

    const timerInterval = setInterval(() => {
      timeLeft -= 1;
      timerText.textContent = formatTime(timeLeft);

      if (timeLeft <= 20) {
        timerBadge.classList.add("warning");
      }

      if (timeLeft <= 0) {
        clearInterval(timerInterval);
        timerText.textContent = "0:00 (Time Expired)";
        // Auto-submit when time expires
        if (form) {
          form.submit();
        }
      }
    }, 1000);
  }
});
