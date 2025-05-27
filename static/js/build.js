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



// Tile placement stuff
function toggleMenu(e) {
  if (e) e.stopPropagation(); // prevent click from bubbling to body
  const menu = document.getElementById("centerMenu");
  menu.classList.toggle("hidden");
  
  // Position menu near the clicked plus button
  if (e && e.target) {
    const rect = e.target.getBoundingClientRect();
    menu.style.left = rect.left + 'px';
    menu.style.top = (rect.bottom + 10) + 'px';
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

// Initialise placement point - will be set properly after DOM loads
let currentPlacementPoint = {
  x: 0,
  y: 0,
  rotation: 0
};

// Set initial placement point after DOM loads
window.addEventListener('DOMContentLoaded', function() {
  const gridContainer = document.querySelector('.middle-panel');
  if (gridContainer) {
    const rect = gridContainer.getBoundingClientRect();
    currentPlacementPoint.x = rect.left + rect.width / 2;
    currentPlacementPoint.y = rect.top + rect.height / 2;
    
    // Also update the initial plus button position
    const initialPlusWrapper = document.getElementById('initial-plus-wrapper');
    if (initialPlusWrapper) {
      initialPlusWrapper.style.left = '50%';
      initialPlusWrapper.style.top = '50%';
    }
  }
});
  
let activePlusButtons = [];

// Called when user clicks a tile type in the popup menu
function placeFromMenu(shapeType) {
    
    // For the initial placement, use the actual position of the initial plus button
    const initialPlus = document.getElementById("initial-plus-wrapper");
    if (initialPlus) {
      const plusButton = initialPlus.querySelector('.plus-button');
      const rect = plusButton.getBoundingClientRect();
      const grid = document.getElementById('grid');
      const gridRect = grid.getBoundingClientRect();
      
      // Convert to grid-relative coordinates
      currentPlacementPoint = {
        x: rect.left + rect.width/2 - gridRect.left,
        y: rect.top + rect.height/2 - gridRect.top,
        rotation: 0
      };
    }
    
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
    
    data.placed.forEach(tile => {
      renderTile(tile.x, tile.y, tile.type, tile.rotation);
      placedShapes.push({x: tile.x, y: tile.y, type: tile.type, rotation: tile.rotation});
    });
    removeAllPlusButtons();
    data.plus_points.forEach(p => {
      createPlusButtonAt(p.x, p.y, p.rotation);
    });

    // Remove initial plus button and hide menu after first shape placement
    const initialPlus = document.getElementById("initial-plus-wrapper");
    if (initialPlus) {
    initialPlus.remove();
    }
    const menu = document.getElementById("centerMenu");
    if (menu) {
    menu.classList.add("hidden");
    }
  });
}

// Create red + sign at given location with rotation
function createPlusButtonAt(x, y, rotation) {


  const plus = document.createElement("div");
  plus.className = "plus-button";
  plus.textContent = "+";
  plus.style.left = `${x}px`;
  plus.style.top = `${y}px`;
  plus.style.transform = `translate(-50%, -50%) rotate(${rotation}deg)`;

  plus.onclick = (e) => { 
    currentPlacementPoint = { x, y, rotation }; // Move the current placement location to the plus button upon being clicked
    toggleMenu(e);
  };

  document.getElementById("grid").appendChild(plus);
  activePlusButtons.push(plus);
}

// Remove all + signs before placing new ones
function removeAllPlusButtons() {
  activePlusButtons.forEach(btn => btn.remove());
  activePlusButtons = [];
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
  }

  if (type === "triangle") {
    // CSS triangles need special positioning due to border-based rendering
    const height = Math.sqrt(3)/2 * TILE_SIDE_LENGTH;
    const centroidFromTop = (2 * height) / 3;  // Distance from top of triangle to centroid
    
    // Position so the centroid is at (x, y)
    tile.style.transform = `translate(-50%, -${centroidFromTop}px) rotate(${rotation}deg)`;
    tile.style.transformOrigin = `50% ${centroidFromTop}px`;
    tile.style.pointerEvents = "none"; // Allow plus buttons to be clickable
  }

  document.getElementById("grid").appendChild(tile);
}

