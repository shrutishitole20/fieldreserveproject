document.addEventListener('DOMContentLoaded', function() {
  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function(e) {
          e.preventDefault();
          const targetId = this.getAttribute('href');
          if (targetId && targetId !== '#') {
              const targetElement = document.querySelector(targetId);
              if (targetElement) {
                  const headerOffset = 80;
                  const elementPosition = targetElement.getBoundingClientRect().top;
                  const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                  
                  window.scrollTo({
                      top: offsetPosition,
                      behavior: 'smooth'
                  });
                  
                  // Close mobile menu if open
                  const navbarCollapse = document.querySelector('.navbar-collapse');
                  if (navbarCollapse.classList.contains('show')) {
                      navbarCollapse.classList.remove('show');
                  }
              }
          }
      });
  });
  
  // Navbar scroll effect
  window.addEventListener('scroll', function() {
      const navbar = document.querySelector('.navbar');
      if (window.scrollY > 10) {
          navbar.classList.add('shadow-sm', 'bg-white');
      } else {
          navbar.classList.remove('shadow-sm', 'bg-white');
      }
  });
  
  // Initialize date picker with min date as today
  const dateInputs = document.querySelectorAll('input[type="date"]');
  const today = new Date().toISOString().split('T')[0];
  
  dateInputs.forEach(input => {
      input.min = today;
  });
  
  // Form validation
  const forms = document.querySelectorAll('.needs-validation');
  
  Array.from(forms).forEach(form => {
      form.addEventListener('submit', event => {
          if (!form.checkValidity()) {
              event.preventDefault();
              event.stopPropagation();
          }
          
          form.classList.add('was-validated');
      }, false);
  });
});
