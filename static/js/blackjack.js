
let playerBalance = 1000;

let playerHand = [];
let dealerHand = [];
let dealerFaceDownCard = null; // This will hold the dealer's face down card element

let gameState = {
  bet: 0,
  gameActive: false,
  playerMinTotal: 0, // Create a running minimum total for the player to calculate a bust before involving backend logic
}


// Helpers to handle operations in the setup of the game
function drawCard() {
  const cardNum = Math.floor(Math.random() * 13) + 1;
  if (cardNum === 1) return 'A';
  if (cardNum === 11) return 'J';
  if (cardNum === 12) return 'Q';
  if (cardNum === 13) return 'K';
  card = cardNum.toString(); // Convert card number to string to stay consistent
  return card; // Return the card value for backend logic processing
}

function findCardSrc(card){ // Card will just be a single character representing the card value/type
  // Generate a random suite (imagine theres like 10 decks, don't bother with card counting)
  const suits = ['S', 'H', 'D', 'C'];
  const suit = suits[Math.floor(Math.random() * suits.length)];

  const cardCode = card + suit; // Combine card value with suit to create a unique identifier based on how each card is named in the elements folder
  return `static/elements/RustCards/${cardCode}.png`; // Return the path to the card image
}

function renderCard(src, side) { // src is desired image src, side can be 'player' or 'dealer'
  // Get the target hand container
  const hand = document.getElementById(`${side}-hand`);

  // Create image element
  const cardImg = document.createElement("img");
  cardImg.src = src;
  cardImg.alt = "card";
  cardImg.className = "card-img";

  // Append the card to the hand
  hand.appendChild(cardImg);
}

function hit() {
  if (!gameState.gameActive) {
    alert("Please start a new round first.");
    return;
  }

  const card = drawCard();
  playerHand.push(card);
  renderCard(findCardSrc(card), "player");

  updateTotal(card); // Update the player's minimum total with the new card
}


function stand() {
  // First flip the dealer card
  flipDealerCard(dealerFaceDownCard);

  // Use a fetch to the python to handle all the logic for the actual game once player actions are resolved
}

function clearHands() {
  document.getElementById("dealer-hand").innerHTML = "";
  document.getElementById("player-hand").innerHTML = "";
}

function updateTotal(cardNum) {
  console.log("total before update: ", gameState.playerMinTotal);
  if (cardNum === 'A') {
    gameState.playerMinTotal += 1; } // Count Ace as 1 for the running minimum total
  else if ((cardNum === 'J') || (cardNum === 'Q') || (cardNum === 'K')) {
    gameState.playerMinTotal += 10;}
  else {
    gameState.playerMinTotal += Number(cardNum); // Add the card number to the player's minimum total
  }
  console.log("total after update: ", gameState.playerMinTotal);

  // Check for bust
  if (gameState.playerMinTotal > 21) {
    console.log("Bust")
    //alert("You busted! Dealer wins."); // Add an animation here for a bust
    showBustAnimation(); // Show bust animation

    gameState.gameActive = false; // End the game
    playerBalance -= bet; // Deduct the bet from player balance
    return "bust"; // Return bust result
  }
  
}

function startNewRound() {
  const betInput = document.getElementById("bet-amount-input");
  bet = parseInt(betInput.value);

  if (isNaN(bet) || bet <= 0) {
    alert("Please enter a valid bet amount.");
    return;
  }

  if (bet > playerBalance) {
    alert(`You only have $${playerBalance}. Please enter a valid bet.`);
    return;
  }

  if (gameState.gameActive) {
    alert("A game is already in progress. Please finish the current game before starting a new one.");
    return;
  }

  gameState.playerMinTotal = 0; // Reset the running player total
  gameState.bet = bet; // Set the bet amount in the game state
  gameState.gameActive = true // Set the game state to true

  
  clearHands(); // Clear previous hands

  // Deal player hand
  playerCard1 = drawCard();
  playerHand.push(playerCard1);
  renderCard(findCardSrc(playerCard1), "player");
  updateTotal(playerCard1); // Update the player's minimum total with the first card

  playerCard2 = drawCard();
  playerHand.push(playerCard2);
  renderCard(findCardSrc(playerCard2), "player");
  updateTotal(playerCard2); // Update the player's minimum total with the second card


  // Deal dealer hand (ironic)
  dealerCard1 = drawCard();
  dealerHand.push(dealerCard1);
  renderCard(findCardSrc(dealerCard1), "dealer");

  dealerCard2 = drawCard();
  dealerHand.push(dealerCard2);
  dealerFaceDownCard = renderCardFaceDown(findCardSrc(dealerCard2), "dealer-hand"); // Render the second dealer card face down

}

function getBalanceChange(result, bet) {
  switch (result) {
    case "blackjack":
    case "player_wins":
    case "dealer_bust":
      return bet;
    case "dealer_blackjack":
    case "dealer_wins":
    case "bust":
      return -bet;
    default:
      return 0;
  }
}


// Animations
function showBustAnimation() { // This is magnificient trust
  const bust = document.getElementById("bust-animation");
  bust.classList.remove("bust-hidden");
  bust.classList.add("bust-visible");

  setTimeout(() => {
    bust.classList.remove("bust-visible");
    bust.classList.add("bust-hidden");
  }, 1600); // Match the duration of the animation
}

// Card flipping
function renderCardFaceDown(realSrc, containerId) {
  const container = document.getElementById(containerId);

  const card = document.createElement('div');
  card.classList.add('flip-card');
  card.setAttribute('data-face', realSrc);

  const inner = document.createElement('div');
  inner.classList.add('flip-inner');

  const front = document.createElement('img');
  front.classList.add('card-face', 'front', 'card-img');
  front.src = 'static/elements/RustCards/back.png';

  const back = document.createElement('img');
  back.classList.add('card-face', 'back', 'card-img');
  back.src = realSrc;

  inner.appendChild(front);
  inner.appendChild(back);
  card.appendChild(inner);
  container.appendChild(card);

  return card;
}


function flipDealerCard(cardElement) {
  cardElement.classList.add('flip');
}
