document.addEventListener('DOMContentLoaded', function () {
  let timer = 25 * 60; // 25分
  let timerInterval = null;
  let isRunning = false;

  const timerValue = document.getElementById('timer-value');
  const startBtn = document.getElementById('btn-start');
  const resetBtn = document.getElementById('btn-reset');
  const timerState = document.getElementById('timer-state');
  const timerCircle = document.getElementById('timer-circle');

  function updateTimerDisplay() {
    const min = Math.floor(timer / 60);
    const sec = timer % 60;
    timerValue.textContent = `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
    updateCircle();
  }

  function updateCircle() {
    const percent = (timer / (25 * 60));
    timerCircle.style.background = `conic-gradient(#7b6ee6 ${percent * 360}deg, #ececfb 0deg)`;
  }

  function startTimer() {
    if (isRunning) return;
    isRunning = true;
    timerState.textContent = '作業中';
    timerInterval = setInterval(() => {
      if (timer > 0) {
        timer--;
        updateTimerDisplay();
      } else {
        clearInterval(timerInterval);
        isRunning = false;
        timerState.textContent = '終了';
      }
    }, 1000);
  }

  function resetTimer() {
    clearInterval(timerInterval);
    timer = 25 * 60;
    isRunning = false;
    timerState.textContent = '作業中';
    updateTimerDisplay();
  }

  startBtn.addEventListener('click', startTimer);
  resetBtn.addEventListener('click', resetTimer);

  updateTimerDisplay();
});
