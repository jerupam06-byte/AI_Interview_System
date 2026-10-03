/**
 * Voice Input Module using browser Web Speech API (SpeechRecognition).
 * Handles microphone permissions, real-time speech-to-text transcript appending,
 * visual recording states, and seamless fallback if browser lacks support.
 */

class VoiceInputController {
  constructor(options = {}) {
    this.buttonId = options.buttonId || "voice-btn";
    this.targetInputId = options.targetInputId || "answer-input";
    this.statusId = options.statusId || "voice-status";
    
    this.recognition = null;
    this.isRecording = false;
    this.btn = document.getElementById(this.buttonId);
    this.targetInput = document.getElementById(this.targetInputId);
    this.statusEl = document.getElementById(this.statusId);

    this.init();
  }

  init() {
    if (!this.btn || !this.targetInput) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      this.btn.title = "Voice recognition is not supported in this browser. Please use text input.";
      this.btn.classList.add("disabled");
      if (this.statusEl) {
        this.statusEl.textContent = "Voice input unavailable (Browser fallback active)";
      }
      this.btn.addEventListener("click", () => {
        alert("Speech Recognition API is not supported in this browser. Text input is fully functional!");
      });
      return;
    }

    try {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
      this.recognition.lang = "en-US";

      this.recognition.onstart = () => {
        this.isRecording = true;
        this.btn.classList.add("recording");
        this.btn.innerHTML = `<span class="recording-dot"></span> Listening... Click to Stop`;
        if (this.statusEl) {
          this.statusEl.textContent = "Listening to your voice... Speak clearly into your mic.";
        }
      };

      this.recognition.onresult = (event) => {
        let finalTranscript = "";
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          }
        }
        if (finalTranscript) {
          const currentText = this.targetInput.value;
          const separator = currentText && !currentText.endsWith(" ") ? " " : "";
          this.targetInput.value = currentText + separator + finalTranscript.trim();
          
          // Trigger input event to update word counter & draft autosave
          this.targetInput.dispatchEvent(new Event("input", { bubbles: true }));
        }
      };

      this.recognition.onerror = (event) => {
        console.warn("Speech recognition error:", event.error);
        this.stop();
        if (this.statusEl) {
          this.statusEl.textContent = `Voice recognition error: ${event.error}. You can continue typing.`;
        }
      };

      this.recognition.onend = () => {
        if (this.isRecording) {
          this.stop();
        }
      };

      this.btn.addEventListener("click", (e) => {
        e.preventDefault();
        if (this.isRecording) {
          this.stop();
        } else {
          this.start();
        }
      });

    } catch (e) {
      console.error("Failed to initialize Speech Recognition:", e);
    }
  }

  start() {
    if (!this.recognition) return;
    try {
      this.recognition.start();
    } catch (e) {
      console.warn("Recognition already started or error:", e);
    }
  }

  stop() {
    this.isRecording = false;
    if (this.btn) {
      this.btn.classList.remove("recording");
      this.btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg> Voice Answer`;
    }
    if (this.statusEl) {
      this.statusEl.textContent = "Voice input ready";
    }
    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (e) {}
    }
  }
}

window.VoiceInputController = VoiceInputController;
