// This file contains login functionality for AJAX requests
// Currently the app uses traditional form submission, but this can be used for future enhancements

async function submitLogin(email, password) {
    try { 
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        // Check if the response is not OK 
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Unknown error occurred');
        }

        const result = await response.json();
        console.log('Login successful');
        return result;
    } catch (error) {
        console.error('Error during login:', error);
        throw error;
    }
}

// Export function for use in other scripts
window.submitLogin = submitLogin;