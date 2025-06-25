
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


// Open a build by ID
function openBuild(buildId) {
    window.location.href = `/build?id=${buildId}`;
}

function createNewBuild() {
    window.location.href = "/build"; // No ID starts a fresh build
}