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
  
      // Get input elements
      const emailEl = document.getElementById('email');
      const passwordEl = document.getElementById('password');
      const confirmEl = document.getElementById('password-confirm');
  
      const email = emailEl ? emailEl.value.trim() : '';
      const password = passwordEl ? passwordEl.value : '';
      const passwordConfirm = confirmEl ? confirmEl.value : '';
  
      // Basic client-side validation
      if (!email || !password || !passwordConfirm) {
        if (messageDiv) {
          messageDiv.className = 'message-box error';
          messageDiv.textContent = 'Please fill in all fields.';
        }
        return;
      }
      if (password !== passwordConfirm) {
        if (messageDiv) {
          messageDiv.className = 'message-box error';
          messageDiv.textContent = 'Passwords do not match.';
        }
        return;
      }
      if (password.length < 8) {
        if (messageDiv) {
          messageDiv.className = 'message-box error';
          messageDiv.textContent = 'Password should be at least 8 characters.';
        }
        return;
      }
  
      // Prepare payload
      const payload = { email, password };
  
      try {
        const response = await fetch('/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            //'X-CSRF-Token': getCookie('csrf_token'), 
          },
          credentials: 'include',
          body: JSON.stringify(payload),
        });
  
        let data = null;
        try {
          data = await response.json();
        } catch (_) {
          data = null;
        }
  
        if (!response.ok) {
          // HTML errors
          const errMsg = data && data.message ? data.message : `Error: ${response.status}`;
          if (messageDiv) {
            messageDiv.className = 'message-box error';
            messageDiv.textContent = errMsg;
          }
          return;
        }
  
        // response.ok is true
        if (data && data.success) {
          // Registration succeeded
          if (messageDiv) {
            messageDiv.className = 'message-box success';
            messageDiv.textContent = 'Registration successful! Redirecting to login...';
          }
          const nextUrl = data.next_url || '/login';
          setTimeout(() => {
            if (nextUrl && nextUrl.startsWith("/") && !nextUrl.startsWith("//")) {
              window.location.href = nextUrl;
            } else {
              window.location.href = "/"; // Default to dashboard in case of redirection to external URL
            }
          }, 1000);
        } else {
          // Backend JSON indicates failure
          const msg = data && data.message ? data.message : 'Registration failed.';
          if (messageDiv) {
            messageDiv.className = 'message-box error';
            messageDiv.textContent = msg;
          }
        }
      } catch (err) {
        console.error('Fetch error during register:', err);
        if (messageDiv) {
          messageDiv.className = 'message-box error';
          messageDiv.textContent = 'Network or server error. Please try again.';
        }
      }
    });
  });
  