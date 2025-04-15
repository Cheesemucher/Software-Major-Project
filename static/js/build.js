let floorCount = 1; // Since the user starts with a floor, the functions should take into account the existence of one floor already so just initialise the JS with one floor

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

function toggleMenu(e) {
    e.stopPropagation(); // prevent click from bubbling to body
    const menu = document.getElementById("centerMenu");
    menu.classList.toggle("hidden");
  }
  
  // Close menu if clicked anywhere outside
  document.addEventListener("click", function (event) {
    const menu = document.getElementById("centerMenu");
    const button = document.querySelector(".plus-button");
  
    // If the click is NOT on the menu or the + button, hide it
    if (!menu.contains(event.target) && !button.contains(event.target)) {
      menu.classList.add("hidden");
    }
  });

function editFloorName() {
  const input = document.getElementById("floorName");
  input.disabled = false;
  input.focus();
  input.select();
}
