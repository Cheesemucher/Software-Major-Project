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

let selectedPlus = document.getElementById("initial-plus-wrapper");

// Tile placement stuff
function toggleMenu(e) {
  console.log(activePlusButtons, "extra active list upon clicking menu") // extra active list for debugging
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
    console.log(selectedPlus, "for deletion")
    removePlusButton(selectedPlus) // Selected plus is also a public variable that is set to a particular plus upon click
    console.log(activePlusButtons, "updated active list")
    requestTilePlacement(shapeType, TILE_SIDE_LENGTH, currentPlacementPoint); // Current placement point information is currently stored as a public variable and not really passed through this function as I am not sure how to pass the position info from the clicked plus button to the HTML that defines the menu then back when the placeFromMenu function is called on click
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
    removeAllPlusButtons()

    console.log(activePlusButtons, "pre adding stuff")
    data.plus_points.forEach(p => {
      // each p is should be: { x: Number, y: Number, rotation: Number }
      activePlusButtons.push(p)
    });
    console.log(activePlusButtons, "post adding stuff")

    activePlusButtons.forEach(button => {
      console.log(button.rotation)
      createPlusButtonAt(button.x, button.y, button.rotation);
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
    selectedPlus = {x, y, rotation}
    console.log(selectedPlus)
  };

  document.getElementById("grid").appendChild(plus);
  //activePlusButtons.push(plus); // Changed the place where buttons are added to the list into the requestTilePlacement function
}

// Remove all + signs before placing new ones
function removeAllPlusButtons() {
  document.querySelectorAll('.plus-button').forEach(div => div.remove());
}

// Remove the single plus button that was clicked on from the activePlusButtons array
function removePlusButton(buttonInfo) {
  console.log("removed button", buttonInfo);

  // Found is a boolean and index is the location of the item if found or '-1' if not found
  const { found, index } = compareButtonInfo(buttonInfo);

  if (found) {
    activePlusButtons.splice(index, 1);
  }
}

function compareButtonInfo(buttonInfo) {
  // Checks for info as the data stored in the list is by arrays of each button's coordinates yet doesn't directly match identical arrays as JS checks where the data is stored and not what the values in the arrays
  const idx = activePlusButtons.findIndex(item =>
    item.x === buttonInfo.x &&
    item.y === buttonInfo.y &&
    item.rotation === buttonInfo.rotation
  );
    console.log(idx)
  return {
    found: idx !== -1,
    index: idx
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
    // CSS triangles need special positioning due to border-based rendering
    const height = Math.sqrt(3)/2 * TILE_SIDE_LENGTH;
    const centroidFromTop = (2 * height) / 3;  // Distance from top of triangle to centroid
    
    // Position so the centroid is at (x, y)
    tile.style.transform = `translate(-50%, -${centroidFromTop}px) rotate(${rotation}deg)`;
    tile.style.transformOrigin = `50% ${centroidFromTop}px`;
    tile.style.pointerEvents = "none"; // Allow plus buttons to be clickable
    tile.style.boxShadow = "inset 0 0 0 1px black"; // Use shadow to create a border as triangles do not follow the HTML div and need CSS concepts to style or smth
  }

  document.getElementById("grid").appendChild(tile);
}

