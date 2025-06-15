document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('register-form');
    const messageDiv = document.getElementById('message');
  
    if (!form) {
      console.error("register.js: #register-form not found");
      return;
    }
    if (!messageDiv) {
      console.warn("register.js: #message div not found; feedback won't show");
    }
  
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
  
      // Grab input elements
      const emailEl = document.getElementById('email');
      const passwordEl = document.getElementById('password');
      const confirmEl = document.getElementById('password-confirm');
  
      const email = emailEl ? emailEl.value.trim() : ''; // WTF this does? I still don't know but the guy told me to put it in so might as well for now
      const password = passwordEl ? passwordEl.value : '';
      const passwordConfirm = confirmEl ? confirmEl.value : '';
  
      // Basic client-side validation
      if (!email || !password || !passwordConfirm) {
        if (messageDiv) messageDiv.textContent = 'Please fill in all fields.';
        return;
      }
      if (password !== passwordConfirm) {
        if (messageDiv) messageDiv.textContent = 'Passwords do not match.';
        return;
      }
      // Optionally: enforce password strength (length, complexity)
      if (password.length < 6) {
        if (messageDiv) messageDiv.textContent = 'Password should be at least 6 characters.';
        return;
      }
  
      // Prepare payload
      const payload = { email, password };
  
      try {
        const response = await fetch('/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            // 'X-CSRFToken': csrfToken, 
          },
          credentials: 'include', // if your app uses cookies/sessions after register
          body: JSON.stringify(payload),
        });
  
        let data = null;
        try {
          data = await response.json();
        } catch (_) {
          data = null;
        }
  
        if (!response.ok) {
          // e.g. 400 for validation error, 409 for conflict, etc.
          const errMsg = data && data.message ? data.message : `Error: ${response.status}`;
          if (messageDiv) messageDiv.textContent = errMsg;
          return;
        }
  
        // Check for response status
        if (data && data.success) {
          // Registration succeeded
          if (messageDiv) {
            messageDiv.style.color = 'green';
            messageDiv.textContent = 'Registration successful! Redirecting to login...';
          }
          // Redirect after short delay, or immediately
          const redirectUrl = data.next_url || '/login';
          setTimeout(() => {
            window.location.href = redirectUrl;
          }, 1000);
        } else {
          // Backend returned JSON but indicated failure
          const msg = data && data.message ? data.message : 'Registration failed.';
          if (messageDiv) {
            messageDiv.style.color = 'red';
            messageDiv.textContent = msg;
          }
        }
      } catch (err) {
        console.error('Fetch error during register:', err);
        if (messageDiv) {
          messageDiv.style.color = 'red';
          messageDiv.textContent = 'Network or server error.';
        }
      }
    });
  });
  