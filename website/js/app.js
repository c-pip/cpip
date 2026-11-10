/**
 * SwarmDroid Website Main Application Logic
 */

document.addEventListener('DOMContentLoaded', () => {
  // --- Code Tabs Switching ---
  const tabButtons = document.querySelectorAll('.tab-btn');
  const codeContents = document.querySelectorAll('.code-content');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');

      tabButtons.forEach(b => b.classList.remove('active'));
      codeContents.forEach(c => c.classList.remove('active'));

      btn.classList.add('active');
      const targetContent = document.getElementById(`tab-${targetTab}`);
      if (targetContent) {
        targetContent.classList.add('active');
      }
    });
  });

  // --- Smooth Scrolling for Navigation Links ---
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;
      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        e.preventDefault();
        targetElement.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });

  // --- Console Greeting ---
  console.log(
    '%c🤖 SwarmDroid Online',
    'color: #00F5D4; font-size: 20px; font-weight: bold; font-family: monospace;'
  );
  console.log(
    '%c"One companion. An entire swarm of intelligence."',
    'color: #B892FF; font-size: 14px; font-style: italic;'
  );
});
