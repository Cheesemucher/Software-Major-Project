let floorCount = 1; // Since the user starts with a floor, the functions should take into account the existence of one floor already so just initialise the JS with one floor
const TILE_SIDE_LENGTH = 80; // How big the shape side lengths will generally be (in px)

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
e.stopPropagation(); // prevent click from bubbling to body
const menu = document.getElementById("centerMenu");
menu.classList.toggle("hidden");
}

// Close menu if clicked anywhere outside, super cool beans
document.addEventListener("click", function (event) {
const menu = document.getElementById("centerMenu");
const button = document.querySelector(".plus-button");

// If the click is NOT on the menu or the + button, hide it
if (!menu.contains(event.target) && !button.contains(event.target)) {
    menu.classList.add("hidden");
}
});

// Reset tile placement point to the center upon initialisation
let currentPlacementPoint = {
  x: 600,
  y: 350,
  rotation: 0, // in degrees because the drawing tool only uses degrees like a true y10 maths student
};
console.log(screen.availHeight)
  
let activePlusButtons = []; // RANDOM ANNOYING LIST come back here if something is messed up by how the plus things are stored but the stuff stored in this list is meant to be temporary to begin with

// Called when user clicks a tile type in the popup menu
function placeFromMenu(shapeType) {
    console.log("Selected shape:", shapeType);  // Just checking
    console.log("First Plus Placement Point:", currentPlacementPoint)
    requestTilePlacement(shapeType, TILE_SIDE_LENGTH, currentPlacementPoint);
  }
  

// Sends shape placement request to Flask
function requestTilePlacement(type, size, originNrotation) {
    console.log("Sending request with:", { // Just check whether the request goes through and is correct
        type,
        size,
        origin: originNrotation
      });
      
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
    data.placed.forEach(tile => renderTile(tile.x, tile.y, tile.type, tile.rotation)); // Gives adjusted places for the shapes to be generated
    removeAllPlusButtons();
    data.plus_points.forEach(p => {
      createPlusButtonAt(p.x, p.y, p.rotation);
    });

    // TEMPORARY CHUNK OF CODE to remove initial static plus and menu if they still exist upon successful tile gen
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

  console.log("New plus button location and rotation", x,y,rotation) // Just debugging where each plus button is generated

  const plus = document.createElement("div");
  plus.className = "plus-button";
  plus.textContent = "+";
  plus.style.left = `${x}px`; // Define a set of coordinates for the + sign in order to store information about where built tiles should go
  plus.style.top = `${y}px`;
  plus.style.transform = `translate(-50%, -50%) rotate(${rotation}deg)`; // Define a rotation to store the orientation of built tiles on top of this + sign. This is basically just electron spin now

  plus.onclick = () => { 
    currentPlacementPoint = { x, y, rotation }; // Move the current placement location to the plus button upon being clicked
    toggleMenu();
  };

  document.getElementById("grid").appendChild(plus);
  activePlusButtons.push(plus);
}

// Remove all + signs before placing new ones
function removeAllPlusButtons() {
  activePlusButtons.forEach(btn => btn.remove());
  activePlusButtons = [];
}

// Shape drawing function -> make it hide both a triangle and a square and only make the desired one visible
function renderTile(x, y, type, rotation) {
  const tile = document.createElement("div");
  tile.className = `tile tile-${type}`;
  tile.style.position = "absolute";
  tile.style.left = `${x}px`;
  tile.style.top = `${y}px`;
  tile.style.transformOrigin = "center"; // Anchor the shape to the div to apply transformations more directly
  tile.style.transform = `translate(-50%, -50%) rotate(${rotation}deg)`; // Set coordinate indexes to the center of the shape and apply rotations about the center as well
  tile.style.zIndex = 2;

  if (type === "square") {
    tile.style.width = `${TILE_SIDE_LENGTH}px`;
    tile.style.height = `${TILE_SIDE_LENGTH}px`;
  }

  if (type === "triangle") {
    tile.style.pointerEvents = "none"; // Let plus buttons be clickable as it overlaps those rn
  }

  document.getElementById("grid").appendChild(tile); // Add the element to the grid div
}



// Show/hide shape selector menu
function toggleMenu() {
  const menu = document.getElementById("centerMenu");
  menu.classList.toggle("hidden");
}

// Click-outside-to-close behavior
document.addEventListener("click", function (e) {
  const menu = document.getElementById("centerMenu");
  const plusBtn = document.querySelector(".plus-button");

  if (!menu.contains(e.target) && !plusBtn.contains(e.target)) {
    menu.classList.add("hidden");
  }
});