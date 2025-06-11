
// This file is still a WIP, I think the login request should be sent from the JS and handled here but currently the HTML just sends a form directly

try { 
    const response = await fetch(SERVER_URL + '/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });

    // Check if the response is not OK 
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Unknown error occurred');
    }


    const result = await response.json(); // Parse JSON response
    console.log('Result session token: ', result.session_token);
    console.log('Result CSRF token: ', result.csrf_token);
    return [result.session_token, result.csrf_token]; 
} catch (error) {
    console.error('Error during registration:', error);
    throw error; // Re-throw the error so it can be handled in handleSubmit
}