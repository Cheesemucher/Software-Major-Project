
// Renaming builds
function startRename(buildId) {
    const span = document.getElementById(`build-name-${buildId}`);
    
    const currentName = span.textContent;
    const input = document.createElement("input");
    input.type = "text";
    input.value = currentName;
    input.className = "inline-edit";
    input.onblur = () => submitRename(buildId, input.value);
    input.onkeydown = (e) => {
      if (e.key === "Enter") input.blur();
    };
  
    span.replaceWith(input);
    input.focus();
  }
  
  async function submitRename(buildId, newName) {
    if (!newName.trim()) return;
  
    const res = await fetch(`/rename-build/${buildId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
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


  function createNewBuild() { 
    const buildName = prompt("Enter a name for this build:");
    if (!buildName) return;
  
    fetch('/create-build', { // Send a save build request but with an empty build save for the initial button
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        build_name: buildName,
        generation_data: { // Empty scaffold for generation data with initial plus button data
          shapes: [],
          plus_buttons: [{
            x: window.innerWidth / 2,
            y: window.innerHeight / 2,
            rotation: 0
          }]
        }
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        console.log("Build made! ID: " + data.build_id);
        window.location.href = `/build?id=${data.build_id}`; // Redirect to the build page with new build loaded
      } else {
        console.log("Error saving build: " + data.message);
      }
    });
  }

// Open a build by ID (currently just redirects with build page with the ID as a query parameter to say which build to load)
function openBuild(buildId) {
    window.location.href = `/build?id=${buildId}`;
}



