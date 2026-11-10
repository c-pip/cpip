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

  // --- Mobile Menu Toggle ---
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const navLinks = document.getElementById('nav-links');
  if (mobileMenuBtn && navLinks) {
    mobileMenuBtn.addEventListener('click', () => {
      navLinks.classList.toggle('open');
      mobileMenuBtn.classList.toggle('active');
    });
    // Close menu when clicking a link
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('open');
        mobileMenuBtn.classList.remove('active');
      });
    });
    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!navLinks.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
        navLinks.classList.remove('open');
        mobileMenuBtn.classList.remove('active');
      }
    });
  }

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
