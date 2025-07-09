
let floorCount = 1;
const TILE_SIDE_LENGTH = 80;
let placedShapes = [];

/*
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
*/


// Infinite panning build environment
const viewport = document.getElementById("viewport");
const canvas = document.getElementById("build-canvas");


// Use Panzoom library for panning and zooming
const panzoom = Panzoom(canvas, {
  maxScale: 5,
  minScale: 0.2,
  contain: 'outside' // Allow panning outside the viewport since we have an 'infinite' building space
});

// Center the view on (5000, 5000)
function centerView() {
  // Wait a short time to ensure DOM is ready
  setTimeout(() => {
    panzoom.pan(window.innerWidth / 2 - 5000, window.innerHeight / 2 - 5000);
    panzoom.zoom(1);
  }, 0); // You can try increasing to 50ms or more if needed
}

viewport.addEventListener('wheel', (event) => { // Just using the panzoom library for this, seems to work so yippee
  panzoom.zoomWithWheel(event, {
    step: 0.02
  });
});





// Initialise placement point - will be set properly after DOM loads
let currentPlacementPoint = {
  x: 5000,
  y: 5000,
  rotation: 0
};

let selectedPlus = null;
let selectedTile = null; // Currently selected tile for deletion or modification

// Tile placement stuff

// Menu toggle functionality
function toggleMenu(e) {
  console.log("Toggling menu at", currentPlacementPoint.x, currentPlacementPoint.y);

  if (e) e.stopPropagation();

  const menu = document.getElementById("centerMenu");
  menu.classList.toggle("hidden");

  if (e && e.target) {
    const rect = e.target.getBoundingClientRect();
    menu.style.left = `${rect.left + rect.width / 2}px`;
    menu.style.top = `${rect.top + rect.height / 2}px`;
    menu.style.transform = 'translate(-50%, -50%)';
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
let activeMinusButtons = []; // Delete buttons

// Called when user clicks a tile type in the popup menu
function placeFromMenu(shapeType) {
  requestTilePlacement(shapeType, TILE_SIDE_LENGTH, currentPlacementPoint);
}

// Sends shape placement request to Flask
function requestTilePlacement(type, size, originNrotation) {
  fetch('/place-shape', {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      'X-CSRF-Token': getCookie('csrf_token'), 
    },
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
      // Close the menu without placing anything if there was an error
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

      drawDeleteButtonAt(tile.type, size, {x: tile.x, y: tile.y, rotation: tile.rotation}); // Draw delete button at the center of the placed tile
      activeMinusButtons.push({type: tile.type, size: size, originNrotation: {x: tile.x, y: tile.y, rotation: tile.rotation}})
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

function deleteTile(type, size, originNrotation) {
  
  
  const { x, y, rotation } = originNrotation;
  /*
  if (type === "square") {
    localPlusPoints = getSquareEdgePositions({ x, y }, rotation, size);
  } else if (type === "triangle") {
    localPlusPoints = getTriangleEdgePositions({ x, y }, rotation, size);
  } else {
    console.log("Unsupported shape type:", type);
    return;
  }

  // Handle tile deletion

  
  localPlusPoints.forEach(p => {
    let newRotation = (p.rotation + 180) % 360; // Flip the rotation by 180 degrees as the deletion generates the buttons backwards
    p.rotation = newRotation; // Update the rotation in the p object (the button object)
    addButton(p, p.x, p.y, newRotation)
  });
  */

  // Remove the desired shape both from array and visually
  placedShapes = placedShapes.filter(shape =>
    !(shape.type === type &&
      shape.x === x &&
      shape.y === y &&
      shape.rotation === rotation));
  const allTiles = document.querySelectorAll('.tile');
  allTiles.forEach(tile => {
    const left = parseFloat(tile.style.left);
    const top = parseFloat(tile.style.top);
    if (Math.abs(left - x) < 1 && Math.abs(top - y) < 1) { 
      tile.remove();
    }
  });

  // Remove the delete button for the deleted shape both from the array and visually as well
  activeMinusButtons = activeMinusButtons.filter(shape =>
    !(shape.originNrotation === originNrotation));

  const allMinus = document.querySelectorAll('.delete-button');
  allMinus.forEach(btn => {
    const left = parseFloat(btn.style.left);
    const top = parseFloat(btn.style.top);
    if (Math.abs(left - x) < 1 && Math.abs(top - y) < 1) {
      btn.remove();
    }
  });

  // Regenerate all + buttons
  regeneratePlusButtons();
}

function regeneratePlusButtons() {
  removeAllPlusButtons(); // Clear all existing ones
  activePlusButtons = [];

  placedShapes.forEach(shape => {
    const { x, y, type, rotation } = shape;

    // Get theoretical edge buttons for this shape
    let edgeButtons = [];
    if (type === "square") {
      edgeButtons = getSquareEdgePositions({ x, y }, rotation);
    } else if (type === "triangle") {
      edgeButtons = getTriangleEdgePositions({ x, y }, rotation);
    }

    edgeButtons.forEach(edge => {
      // Simulate placing a new square at this button
      const squareCentre = getSquareCentre(edge.x, edge.y, edge.rotation);
      const triangleCentre = getTriangleCentre(edge.x, edge.y, edge.rotation);

      const overlapsSquare = checkOverlapAny(squareCentre, "square");
      const overlapsTriangle = checkOverlapAny(triangleCentre, "triangle");

      if (!overlapsSquare || !overlapsTriangle) {
        addButton(edge, edge.x, edge.y, edge.rotation);
        drawPlusButtonAt(edge.x, edge.y, edge.rotation);
      }
    });
  });
}

// Helper to simulate overlap like your Python version
function checkOverlapAny(newShape, type) {
  const buffer = 5; // same thresholds from backend logic
  return placedShapes.some(existing => {
    const dx = existing.x - newShape.x;
    const dy = existing.y - newShape.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    let minDist = 0;
    if (existing.type === "square" && type === "square") minDist = 75;
    else if (existing.type === "triangle" && type === "triangle") minDist = 35;
    else minDist = 58;

    return distance < minDist;
  });
}

function renderBuild(generation_data) {
  console.log("Attempt rendering build with generation data:", generation_data);

  placedShapes = generation_data.shapes; // Override the array for current placed shapes with those from the generation data
  activePlusButtons = generation_data.plus_buttons; 
  console.log("buttons rn", activePlusButtons);

  // Render shapes
  placedShapes.forEach(shape => {
    renderTile(shape.x, shape.y, shape.type, shape.rotation);
    drawDeleteButtonAt(shape.type, TILE_SIDE_LENGTH, {x: shape.x, y: shape.y, rotation: shape.rotation});
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
    return "button added";
  }
}

// Draw red + sign at given location with rotation
function drawPlusButtonAt(x, y, rotation) {
  console.log("Drawing plus button at", x, y, "with rotation", rotation);
  const plus = document.createElement("div");
  plus.className = "plus-button";
  plus.textContent = "+";
  plus.style.left = `${x}px`;
  plus.style.top = `${y}px`;
  plus.style.transform = `translate(-50%, -50%) rotate(${rotation}deg)`;

  plus.onclick = (e) => {
    e.stopPropagation(); // Prevent document click listener from closing the menu immediately
    currentPlacementPoint = { x, y, rotation };
    toggleMenu(e);
    selectedPlus = {x, y, rotation};
  };

  document.getElementById("build-canvas").appendChild(plus);
}

// Same deal but for a delete button that should be in the centre of a generated shape
function drawDeleteButtonAt(type, size, originNrotation) {
  const { x, y, rotation } = originNrotation;
  console.log("Drawing delete button at", x, y, "with rotation", rotation);

  const minus = document.createElement("div");
  minus.className = "delete-button";
  minus.textContent = "🗑";  // Trash can emoji type shii -> maybe do a X emoji or smth

  minus.style.left = `${x}px`;
  minus.style.top = `${y}px`;
  minus.style.transform = `translate(-50%, -50%) rotate(${rotation}deg)`;

  minus.onclick = (e) => {
    e.stopPropagation(); // Prevent outside click listeners from interfering
    deleteTile(type, size, originNrotation); // Delete tile + cleanup
  };

  document.getElementById("build-canvas").appendChild(minus);
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

  document.getElementById("build-canvas").appendChild(tile);
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
        "Content-Type": "application/json",
        'X-CSRF-Token': getCookie('csrf_token'),
      },
      body: JSON.stringify({ generation_data: generationData })
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
  } catch (error) {
    console.error("Error saving build:", error);
  }
}




// Called on page load
window.addEventListener('DOMContentLoaded', async () => {
  console.log("centering view");
  centerView()

  console.log("begginning render build")
  try {
    const res = await fetch('/selected-build', { // Retrieve the selected build data from the server upon page load
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'X-CSRF-Token': getCookie('csrf_token'),
       }
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


// Helper functions to find all plus buttons from a given shape type and its position, TODO: Might replace the call to backend with these functions for the actual shape generation too in the future to prevent clutter since I am not using that to store shapes anyway

// Basically converted the helper functions in the shape.py file into JS code
function getSquareEdgePositions(centre, rotation) {
  const rad = rotation * Math.PI / 180;
  const out = [];
  for (let i = 0; i < 4; i++) {
    const a = rad + i * (Math.PI / 2);
    out.push({
      x: centre.x + (TILE_SIDE_LENGTH / 2) * Math.sin(a),
      y: centre.y - (TILE_SIDE_LENGTH / 2) * Math.cos(a),
      rotation: (a * 180 / Math.PI) % 360
    });
  }
  return out;
}

function getTriangleEdgePositions(centre, rotation) {
  const height = Math.sqrt(3) / 2 * TILE_SIDE_LENGTH;
  const d = height / 3;
  const base = rotation * Math.PI / 180 + Math.PI;
  return [0, 2 / 3 * Math.PI, -2 / 3 * Math.PI].map(offset => {
    const a = base + offset;
    return {
      x: centre.x + d * Math.sin(a),
      y: centre.y - d * Math.cos(a),
      rotation: (a * 180 / Math.PI) % 360
    };
  });
}

function getSquareCentre(click_x, click_y, rotation) {
  const rotationRad = rotation * Math.PI / 180;
  const shiftX = (TILE_SIDE_LENGTH / 2) * Math.sin(rotationRad);
  const shiftY = -(TILE_SIDE_LENGTH / 2) * Math.cos(rotationRad);

  return {
    x: click_x + shiftX,
    y: click_y + shiftY
  };
}

// Calculates triangle center from edge click position
function getTriangleCentre(click_x, click_y, rotation) {
  const height = (Math.sqrt(3) / 2) * TILE_SIDE_LENGTH;
  const distFromBaseToCentre = height / 3;
  const rotationRad = rotation * Math.PI / 180;

  const shiftX = distFromBaseToCentre * Math.sin(rotationRad);
  const shiftY = -distFromBaseToCentre * Math.cos(rotationRad);

  return {
    x: click_x + shiftX,
    y: click_y + shiftY
  };
}