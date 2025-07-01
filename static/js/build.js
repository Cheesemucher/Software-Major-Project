let floorCount = 1;
const TILE_SIDE_LENGTH = 80;
let placedShapes = [];

// Floor menu stuff
function addFloor() {
  floorCount++;
  const floorList = document.getElementById("floorList");

  const wrapper = document.createElement("div");
  wrapper.className = "floor-label";

  const input = document.createElement("input");
  input.type = "text";
  input.value = `Floor ${floorCount}`;
  input.disabled = true;

  const btn = document.createElement("button");
  btn.innerText = "✎";
  btn.onclick = () => {
    input.disabled = false;
    input.focus();
    input.select();
  };

  wrapper.appendChild(input);
  wrapper.appendChild(btn);
  floorList.appendChild(wrapper);
}

function editFloorName() {
    const input = document.getElementById("floorName");
    input.disabled = false;
    input.focus();
    input.select();
  }


// Initialise placement point - will be set properly after DOM loads
let currentPlacementPoint = {
  x: 0,
  y: 0,
  rotation: 0
};

let selectedPlus = null;

// Tile placement stuff
function toggleMenu(e) {
  if (e) e.stopPropagation(); // prevent click from bubbling to body
  const menu = document.getElementById("centerMenu");
  menu.classList.toggle("hidden");

  // Position menu near the clicked plus button
  if (e && e.target) {
    const rect = e.target.getBoundingClientRect();
    menu.style.left = (currentPlacementPoint.x - 50) + 'px';
    menu.style.top = (currentPlacementPoint.y - 30) + 'px';
    menu.style.transform = 'none';
  }
}

// Close menu if clicked anywhere outside
document.addEventListener("click", function (event) {
  const menu = document.getElementById("centerMenu");
  const plusButtons = document.querySelectorAll(".plus-button");

  // Check if click is on any plus button
  let clickedOnPlus = false;
  plusButtons.forEach(btn => {
    if (btn.contains(event.target)) clickedOnPlus = true;
  });

  // If the click is NOT on the menu or any + button, hide it
  if (!menu.contains(event.target) && !clickedOnPlus) {
    menu.classList.add("hidden");
  }
});

// Set initial placement point after DOM loads
window.addEventListener('DOMContentLoaded', function() {
  const gridContainer = document.querySelector('.middle-panel');
  if (gridContainer) {
    const rect = gridContainer.getBoundingClientRect();
    currentPlacementPoint.x = rect.left + rect.width / 2;
    currentPlacementPoint.y = rect.top + rect.height / 2;
  }
});

let activePlusButtons = [];

// Called when user clicks a tile type in the popup menu
function placeFromMenu(shapeType) {
  requestTilePlacement(shapeType, TILE_SIDE_LENGTH, currentPlacementPoint);
}

// Sends shape placement request to Flask
function requestTilePlacement(type, size, originNrotation) {
  fetch('/place-shape', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      type,
      size,
      x: originNrotation.x,
      y: originNrotation.y,
      rotation: originNrotation.rotation
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.error) {
      console.log("Error placing shape:", data.error);
      // Close the menu without placing anything
      const menu = document.getElementById("centerMenu");
      if (menu) {
        menu.classList.add("hidden");
      }
      return;
    }

    // Handle tile placing
    data.placed.forEach(tile => {
      renderTile(tile.x, tile.y, tile.type, tile.rotation);
      placedShapes.push({x: tile.x, y: tile.y, type: tile.type, rotation: tile.rotation});
    });

    // Add plus buttons to activePlusButtons array
    data.plus_points.forEach(p => {
      addButton(p, p.x, p.y, p.rotation)
    });

    // Get rid of all the existing buttons before redrawing them
    removeAllPlusButtons();
    removePlusButton(selectedPlus); // Remove the plus button that was clicked on in case it survived somehow as it has a habit of doing so
    // Real reason is this function removes it from the array so in the case of the first plus button where only one needs to be removed, this function does so

    activePlusButtons.forEach(button => {
      drawPlusButtonAt(button.x, button.y, button.rotation);
    });

    // Hide menu again after first shape placement
    const menu = document.getElementById("centerMenu");
    if (menu) {
      menu.classList.add("hidden");
    }
  });
}


function renderBuild(generation_data) {
  console.log("Attempt rendering build with generation data:", generation_data);

  placedShapes = generation_data.shapes; // Override the array for current placed shapes with those from the generation data
  activePlusButtons = generation_data.plus_buttons; 

  // Render shapes
  placedShapes.forEach(shape => {
    renderTile(shape.x, shape.y, shape.type, shape.rotation);
  });

  // Render plus buttons
  activePlusButtons.forEach(btn => {
    drawPlusButtonAt(btn.x, btn.y, btn.rotation);
  });
}


function addButton(button,x,y,rotation) { 
  buttonInfo = {x, y, rotation}

  // First check if this is the first shape being placed as it will need all sides to have a button if so
  if (placedShapes.length <= 1) {
    activePlusButtons.push(button); // Add the first button to the list
    return; // End the function here (Special privileges, probably some form of nepotism)
  }

  const { found, index } = compareButtonInfo(buttonInfo); // Check if each new button to add is already in the list

  if (found) {
    activePlusButtons.splice(index, 1); // Remove both if found (pair annihilation)
  }

  else {
    activePlusButtons.push(button); // Otherwise add it to the list
  }
}

// Draw red + sign at given location with rotation
function drawPlusButtonAt(x, y, rotation) {
  const plus = document.createElement("div");
  plus.className = "plus-button";
  plus.textContent = "+";
  plus.style.left = `${x}px`;
  plus.style.top = `${y}px`;
  plus.style.transform = `translate(-50%, -50%) rotate(${rotation}deg)`;

  plus.onclick = (e) => { 
    currentPlacementPoint = { x, y, rotation };
    toggleMenu(e);
    selectedPlus = {x, y, rotation}
  };

  document.getElementById("grid").appendChild(plus);
}

// Remove all + buttons before placing new ones
function removeAllPlusButtons() {
  document.querySelectorAll('.plus-button').forEach(div => div.remove());
}

// Remove the single plus button that was clicked on from the activePlusButtons array
function removePlusButton(buttonInfo) {
  console.log("removed button", buttonInfo);

  const { found, index } = compareButtonInfo(buttonInfo);

  if (found) {
    console.log("button found in list position", index)
    activePlusButtons.splice(index, 1);
  }
}

function compareButtonInfo(buttonInfo) {
  const BOUNDS = TILE_SIDE_LENGTH / 3;

  const id = activePlusButtons.findIndex(item =>
    Math.abs(item.x - buttonInfo.x) <= BOUNDS &&
    Math.abs(item.y - buttonInfo.y) <= BOUNDS
  );

  return {
    found: id !== -1,
    index: id
  };
}

// Shape drawing function
function renderTile(x, y, type, rotation) {
  const tile = document.createElement("div");
  tile.className = `tile tile-${type}`;
  tile.style.position = "absolute";
  tile.style.left = `${x}px`;
  tile.style.top = `${y}px`;
  tile.style.transformOrigin = "center";
  tile.style.zIndex = 2;

  if (type === "square") {
    tile.style.width = `${TILE_SIDE_LENGTH}px`;
    tile.style.height = `${TILE_SIDE_LENGTH}px`;
    tile.style.transform = `translate(-50%, -50%) rotate(${rotation}deg)`;
    tile.style.boxSizing = "border-box";
    tile.style.border = "0.5px solid black";
  }

  if (type === "triangle") {
    const height = Math.sqrt(3)/2 * TILE_SIDE_LENGTH;
    const centroidFromTop = (2 * height) / 3;

    tile.style.transform = `translate(-50%, -${centroidFromTop}px) rotate(${rotation}deg)`;
    tile.style.transformOrigin = `50% ${centroidFromTop}px`;
    tile.style.pointerEvents = "none";
    tile.style.boxShadow = "inset 0 0 0 1px black";
  }

  document.getElementById("grid").appendChild(tile);
}

// Send the current build to the Flask backend server to be saved into the current build object's database
async function saveBuild() {

  const generationData = { // Define the generation data as a JS object to be sent to the server as that is the standardised format it is to be stored now
    shapes: placedShapes,
    plus_buttons: activePlusButtons
  };

  try {
    const response = await fetch("/save-build", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ generation_data: generationData })
    });

    const result = await response.json();
    if (result.success) {
      console.log("Build saved successfully.");
    } else {
      console.error("Failed to save build:", result.message);
    }
  } catch (error) {
    console.error("Error saving build:", error);
  }
}


window.addEventListener('DOMContentLoaded', async () => {
  try {
    const res = await fetch('/selected-build', { // Retrieve the selected build data from the server upon page load
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });

    const result = await res.json();
    if (!result.success) {
      console.error("Failed to load build:", result.message);
      return;
    }

    renderBuild(result.generation_data); // Render the build with desired data upon page load
  } catch (error) {
    console.error("Error fetching build data:", error);
  }
});