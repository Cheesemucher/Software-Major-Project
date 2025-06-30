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

    // Handle Plus button generation
    data.plus_points.forEach(p => {
      addButton(p, p.x, p.y, p.rotation)
    });

    // Get rid of all the existing buttons before redrawing them
    removeAllPlusButtons()
    removePlusButton(selectedPlus)

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


function renderBuild() {
  const shapes = generation_data.shapes || [];
  let plus_buttons = generation_data.plus_buttons || []; // TODO: Make the default plus button array the single initial plus button

  // If build is completely empty, generate default center + button
  if (shapes.length === 0 && plus_buttons.length === 0) {
    const grid = document.getElementById('grid');
    const gridRect = grid.getBoundingClientRect();
    const centerX = gridRect.width / 2;
    const centerY = gridRect.height / 2;
    plus_buttons = [{ x: centerX, y: centerY, rotation: 0 }];
  }

  // Render shapes
  shapes.forEach(shape => {
    renderTile(shape.x, shape.y, shape.type, shape.rotation);
    placedShapes.push(shape);
  });

  // Render plus buttons
  plus_buttons.forEach(btn => {
    drawPlusButtonAt(btn.x, btn.y, btn.rotation);
    activePlusButtons.push(btn);
  });
}


function addButton(button,x,y,rotation) { 
  buttonInfo = {x, y, rotation}
  const { found, index } = compareButtonInfo(buttonInfo); // Check if each new button to add is already in the list

  if (found) {
    activePlusButtons.splice(index, 1); // Remove it if found
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

function saveBuild() {
  const buildName = prompt("Enter a name for this build:");
  if (!buildName) return;

  fetch('/save-build', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      build_name: buildName,
      generation_data: {
        shapes: placedShapes,
        plus_buttons: activePlusButtons
      }
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      alert("Build saved! ID: " + data.build_id);
    } else {
      alert("Error saving build: " + data.message);
    }
  });
}


window.addEventListener('DOMContentLoaded', function () {
  if (generation_data && generation_data.length > 0) {
    renderBuild();
  }
});