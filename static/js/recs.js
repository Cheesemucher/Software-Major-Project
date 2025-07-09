

// Create a saved copy of the meta build for users to edit
async function makeCopy(build) { // build is the clicked build object with keys: title, youtube_link, generation_data
    const build_name = build.title || "New Build Copy"; // The autofill text extension made the or gate but might be unecessary TODO come back and delete this comment or the or gate
    const generation_data = build.generation_data || {};
    
    const response = await fetch('/copy-build', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': getCookie('csrf_token'),
        },
        body: JSON.stringify({
            name: build_name,
            generation_data: generation_data,
        }),
    });
    const result = await response.json();
    if (result.success) {
      console.log("Build saved successfully.");
      // Exit back to the saves page after successful save
      const nextUrl = '/saves'; 
      if (nextUrl && nextUrl.startsWith("/") && !nextUrl.startsWith("//")) {
              window.location.href = nextUrl;
            } else {
              window.location.href = "/"; // Default to dashboard in case of redirection to external URL
            }

    } else {
      console.error("Failed to save build:", result.message);
    }
}

async function returnToBuild() {
    try {
    response = await fetch('/get-current-bID', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': getCookie('csrf_token'),
        },
    });
    const result = await response.json();
    if (result.success) {
      const buildId = result.build_id;
      
      const nextUrl = `/build?id=${buildId}`
      // Redirect to the build page with desired build loaded
      if (nextUrl && nextUrl.startsWith("/") && !nextUrl.startsWith("//")) {
        window.location.href = nextUrl;
      } 
      else {
        window.location.href = "/"; // Default to dashboard in case of redirection to external URL
      }

    } else {
      console.error("Failed to get build:", result.message);
    }
    } catch (error) {
    console.error("Failed to return to build page:", error);
    }
}