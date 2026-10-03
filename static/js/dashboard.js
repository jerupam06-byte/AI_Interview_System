/**
 * Dashboard Analytics Module (Chart.js)
 * Renders score performance trends and skill gap breakdown.
 */

document.addEventListener("DOMContentLoaded", () => {
  // 1. Performance Trend Chart
  const scoreCanvas = document.getElementById("scoreTrendChart");
  if (scoreCanvas && window.Chart) {
    const rawDates = scoreCanvas.dataset.dates ? JSON.parse(scoreCanvas.dataset.dates) : [];
    const rawScores = scoreCanvas.dataset.scores ? JSON.parse(scoreCanvas.dataset.scores) : [];

    const ctx = scoreCanvas.getContext("2d");
    new Chart(ctx, {
      type: "line",
      data: {
        labels: rawDates.length > 0 ? rawDates : ["Session 1", "Session 2", "Session 3"],
        datasets: [{
          label: "Overall Score (%)",
          data: rawScores.length > 0 ? rawScores : [65, 78, 88],
          borderColor: "#06B6D4",
          backgroundColor: "rgba(6, 182, 212, 0.12)",
          borderWidth: 2.5,
          fill: true,
          tension: 0.35,
          pointBackgroundColor: "#2563EB",
          pointBorderColor: "#FFFFFF",
          pointRadius: 4,
          pointHoverRadius: 6,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            min: 0,
            max: 100,
            grid: { color: "rgba(255, 255, 255, 0.06)" },
            ticks: { color: "#94A3B8" }
          },
          x: {
            grid: { display: false },
            ticks: { color: "#94A3B8" }
          }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "#1E293B",
            titleColor: "#F8FAFC",
            bodyColor: "#94A3B8",
            borderColor: "#334155",
            borderWidth: 1,
            padding: 10,
          }
        }
      }
    });
  }

  // 2. Skill Gap Radar / Bar Chart
  const gapCanvas = document.getElementById("skillGapChart");
  if (gapCanvas && window.Chart) {
    const rawLabels = gapCanvas.dataset.labels ? JSON.parse(gapCanvas.dataset.labels) : [];
    const rawValues = gapCanvas.dataset.values ? JSON.parse(gapCanvas.dataset.values) : [];

    const defaultLabels = ["Python", "SQL", "Machine Learning", "NLP", "HR & Communication"];
    const defaultValues = [82, 70, 75, 68, 85];

    const ctx = gapCanvas.getContext("2d");
    new Chart(ctx, {
      type: "radar",
      data: {
        labels: rawLabels.length > 0 ? rawLabels : defaultLabels,
        datasets: [{
          label: "Skill Mastery (%)",
          data: rawValues.length > 0 ? rawValues : defaultValues,
          backgroundColor: "rgba(37, 99, 235, 0.25)",
          borderColor: "#3B82F6",
          pointBackgroundColor: "#06B6D4",
          pointBorderColor: "#FFFFFF",
          borderWidth: 2,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            min: 0,
            max: 100,
            angleLines: { color: "rgba(255, 255, 255, 0.08)" },
            grid: { color: "rgba(255, 255, 255, 0.08)" },
            pointLabels: {
              color: "#F8FAFC",
              font: { size: 11, weight: "600" }
            },
            ticks: {
              display: false,
              stepSize: 20
            }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }
});
