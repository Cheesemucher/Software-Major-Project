
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
      event.preventDefault();  // stop default form submission to use a JS fetch instead

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
            // 'X-CSRF-Token': getCookie('csrf_token'),  Dont need right
          },
          body: JSON.stringify(payload),
          credentials: 'include',  // for cookies
        });
  
        // Parse JSON response
        try {
            data = await response.json();
          } catch (parseErr) {
            console.warn('Could not parse JSON:', parseErr);
          }

        if (!response.ok) {
            // HTTP level error
            const msg = data && data.message ? data.message : `Error: ${response.status}`;
            if (messageDiv) {
              messageDiv.className = 'message-box error';
              messageDiv.textContent = msg;
            }
            return;
          }

        if (data && data.success) {
            if (messageDiv) {
              messageDiv.className = 'message-box success';
              messageDiv.textContent = 'Login successful! Redirecting...';
            }
            const nextUrl = data.next_url 
            // Only allow relative URLs starting with "/" and not "//" (which would be external) to prevent invalid forwarding
            if (nextUrl && nextUrl.startsWith("/") && !nextUrl.startsWith("//")) {
              window.location.href = nextUrl;
            } else {
              window.location.href = "/"; // Fallback route (e.g., dashboard)
            }
          } 
          else {
            // response was 2xx but JSON indicates failure or missing fields
            const msg = data && data.message ? data.message : 'Login failed';
            if (messageDiv) {
              messageDiv.className = 'message-box error';
              messageDiv.textContent = msg;
            }
          }
        } 
        catch (err) {
          console.error('Fetch error:', err);
          if (messageDiv) {
            messageDiv.className = 'message-box error';
            messageDiv.textContent = 'Network or server error. Please try again.';
          }
        }
      
    });
  });
  
