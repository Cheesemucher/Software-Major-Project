
// Intercept the submitted HTML form and instead use JS to send a proper fetch request IM SORRY FOR NOT USING REACT NOW ;-;
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('login-form');
    const messageDiv = document.getElementById('message');
  
    // Basic client-side validation to check for empty form on init
    if (!form) {
        console.error("Cannot find #login-form in DOM");
        return;
      }
    if (!messageDiv) {
        console.warn("Cannot find #message div; status messages won't show.");
      }

    form.addEventListener('submit', async (event) => {
      event.preventDefault();  // stop default form submission

      // Collect input values
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;
  
      if (!email || !password) {
        messageDiv.textContent = 'Username and password are required.';
        return;
      }
  
      try {
        const payload = { email, password };
  
        const response = await fetch('/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            // CSRF TOKEN when it is created
          },
          body: JSON.stringify(payload),
          credentials: 'include',  // for cookies
        });
  
        if (!response.ok) {
          // HTTP-level error (e.g. 400, 401, 500)
          const errorData = await response.json().catch(() => null);
          const errMsg = (errorData && errorData.message) || `Error: ${response.status}`;
          messageDiv.textContent = errMsg;
          return;
        }
  
        // Parse JSON response
        const data = await response.json();
  
        if (data.success) {
          // Login succeeded. You might redirect or update UI.
          messageDiv.textContent = 'Login successful! Redirecting...';
          // e.g.: window.location.href = '/dashboard';
        } else {
          // Backend indicates failure
          messageDiv.textContent = data.message || 'Login failed';
        }
      } catch (err) {
        console.error('Fetch error:', err);
        messageDiv.textContent = 'Network or server error. Please try again.';
      }
    });
  });
  
