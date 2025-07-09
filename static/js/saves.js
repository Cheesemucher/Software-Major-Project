
// Renaming builds
function startRename(buildId) {
    const span = document.getElementById(`build-name-${buildId}`);
    
    const currentName = span.textContent;
    const input = document.createElement("input");
    input.type = "text";
    input.value = currentName;
    input.className = "inline-edit";
    input.onblur = () => submitRename(buildId, input.value); // This called function updates the database with renamed build when the input loses focus (enter key for this case)
    input.onkeydown = (e) => {
      if (e.key === "Enter") input.blur();
    };
  
    span.replaceWith(input);
    input.focus();
  }
  
async function submitRename(buildId, newName) {
  if (!newName.trim()) return;

  const res = await fetch(`/rename-build/${buildId}`, { // Send request to the python to alter the database
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      'X-CSRF-Token': getCookie('csrf_token'),
      },
    body: JSON.stringify({ name: newName })
  });

  const result = await res.json();

  const input = document.querySelector(`input.inline-edit`);
  const span = document.createElement("span");
  span.id = `build-name-${buildId}`;
  span.className = "editable-name";
  span.textContent = newName;

  if (input) input.replaceWith(span);

  if (!result.success) {
    alert("Rename failed: " + result.message);
  }
}

// Same deal but for the description
function editDescription(buildId) {
  const descBox = document.querySelector(`#description-${buildId}`);
  const currentDesc = descBox.textContent.trim();

  const textarea = document.createElement("textarea");
  textarea.className = "description-edit";
  textarea.value = currentDesc;

  textarea.onblur = () => submitDescription(buildId, textarea.value);
  textarea.onkeydown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      textarea.blur();
    }
  };
  descBox.replaceWith(textarea);
  textarea.focus();
}

async function submitDescription(buildId, newDesc) {
  if (!newDesc.trim()) return;

  const res = await fetch(`/update-description/${buildId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": getCookie("csrf_token")
    },
    body: JSON.stringify({ description: newDesc })
  });

  const result = await res.json();

  const textarea = document.querySelector(`textarea.description-edit`);
  const newSpan = document.createElement("div");
  newSpan.id = `description-${buildId}`;
  newSpan.className = "description-text";
  newSpan.textContent = newDesc;

  if (textarea) textarea.replaceWith(newSpan);

  if (!result.success) {
    alert("Description failed: " + result.message);
  }
}



async function deleteBuild(buildId) {
  const confirmed = confirm("Are you sure you want to delete this build?");
  if (!confirmed) return;

  const res = await fetch(`/delete-build/${buildId}`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      'X-CSRF-Token': getCookie('csrf_token'),
    }
  });

  const result = await res.json();

  if (result.success) {
    // Reload the page to get rid of the deleted card
    location.reload();
  } else {
    alert("Deletion failed: " + result.message);
  }
}



function createNewBuild() { 
  const buildName = prompt("Enter a name for this build:");
  if (!buildName) return;

  fetch('/create-build', { // Send a save build request but with an empty build save for the initial button
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      'X-CSRF-Token': getCookie('csrf_token'),
    },
    body: JSON.stringify({
      build_name: buildName,
      generation_data: { // Empty scaffold for generation data with initial plus button data
        shapes: [],
        plus_buttons: [{
          x: 5000, // Center of the canvas
          y: 5000,
          rotation: 0
        }]
      }
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      const nextUrl = `/build?id=${data.build_id}`
      console.log("Build made! ID: " + data.build_id);
      // Redirect to the build page with new build loaded
      if (nextUrl && nextUrl.startsWith("/") && !nextUrl.startsWith("//")) {
        window.location.href = nextUrl;
      } else {
        window.location.href = "/"; // Default to dashboard in case of redirection to external URL
            }
    } else {
      console.log("Error saving build: " + data.message);
    }
  });
}

// Open a build by ID (currently just redirects with build page with the ID as a query parameter to say which build to load)
function openBuild(buildId) {
    const nextUrl = `/build?id=${buildId}`
    // Redirect to the build page with desired build loaded
    if (nextUrl && nextUrl.startsWith("/") && !nextUrl.startsWith("//")) {
      window.location.href = nextUrl;
    } 
    else {
      window.location.href = "/"; // Default to dashboard in case of redirection to external URL
    }
}



