
let playerBalance = 1000;

let playerHand = [];
let dealerHand = [];
let dealerFaceDownCard = null; // This will hold the dealer's face down card element

let gameState = {
  bet: 0,
  gameActive: false,
  multiplier: 1,
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

function findBlackjack(card1, card2) { // Just checks if starting hands add to 21 to call blackjack, copilot autofilled the function so if it doesnt work come back to this
  // Convert a card value to its numerical Blackjack value
  function getCardValue(card) {
    if (card === 'A') return 11;
    if (['K', 'Q', 'J'].includes(card)) return 10;
    const num = Number(card);
    return isNaN(num) ? 0 : num;
  }

  const val1 = getCardValue(card1);
  const val2 = getCardValue(card2);

  return val1 + val2 === 21;
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

function updateUIStats() {
  const multiplierElem = document.getElementById("multiplier");
  const potElem = document.getElementById("pot");
  const balanceElem = document.getElementById("player-balance");

  if (multiplierElem) multiplierElem.textContent = `x${gameState.multiplier} multiplier`;
  if (potElem) potElem.textContent = `Pot: ${gameState.bet} Scrap`;
  if (balanceElem) balanceElem.textContent = `Balance: ${playerBalance} Scrap`;
}

function endGame(){
  gameState.multiplier = 1
  gameState.bet = 0
  gameState.gameActive = false
  updateUIStats()
  playerHand = []
  dealerHand = []
  dealerFaceDownCard = null
}

function clearHands() {
  document.getElementById("dealer-hand").innerHTML = "";
  document.getElementById("player-hand").innerHTML = "";
}

function updateTotal(cardNum) {
  if (cardNum === 'A') {
    gameState.playerMinTotal += 1; } // Count Ace as 1 for the running minimum total
  else if ((cardNum === 'J') || (cardNum === 'Q') || (cardNum === 'K')) {
    gameState.playerMinTotal += 10;}
  else {
    gameState.playerMinTotal += Number(cardNum); // Add the card number to the player's minimum total
  }

  // Check for bust
  if (gameState.playerMinTotal > 21) {
    console.log("Bust")
    //alert("You busted! Dealer wins."); // Add an animation here for a bust
    showGameMessage("Bust!", "#FF4E4E"); // Show bust animation

    playerBalance -= gameState.multiplier * gameState.bet; // Deduct the bet from player balance
    endGame()
  }
  
}
// Just allow pauses between card reveals for suspense
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}




// Actual game functionality
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

async function stand() {
  if (!gameState.gameActive) {
    alert("Please start a new round first.");
    return;
  }

  // First flip the dealer card
  flipDealerCard(dealerFaceDownCard);

  // Wait a bit, let reader shiver in their timbers
  await sleep(1000)

  // Deal dealer and resolve game
  const response = await fetch('/blackjack/resolve-game', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': getCookie('csrf_token'),
    },
    body: JSON.stringify({
      playerHand: playerHand,
      dealerHand: dealerHand,
    }),
  });

  const data = await response.json();

  const result = data.result;
  const dealerCards = data.dealer_cards;
  console.log(dealerCards)

  // Render dealer cards
  dealerCards.forEach(card => {
    renderCard(findCardSrc(card), "dealer");
    });

  // Handle game result
  switch (result) {
    case "Player Wins":
      showGameMessage("You win!", "#4EFF89"); // green
      playerBalance += gameState.multiplier * gameState.bet;
      break;
    case "Dealer Wins":
      showGameMessage("Dealer wins.", "#FF4E4E"); // red
      playerBalance -= gameState.multiplier * gameState.bet;
      break;
    case "Dealer Busts":
      showGameMessage("Dealer busts! You win!", "#4EFF89"); // yellow
      playerBalance += gameState.multiplier * gameState.bet;
      break;
    case "Push":
      showGameMessage("Push", "#FFD64E");
      break;
  }
  // End round stuff
  endGame()
}

function startNewRound() {
  const betInput = document.getElementById("bet-amount-input");
  bet = parseInt(betInput.value);

  if (isNaN(bet) || bet <= 0) {
    alert("Please enter a valid bet amount.");
    return;
  }

  if (bet > playerBalance) {
    alert(`You only have ${playerBalance} scrap. Please enter a valid bet.`);
    return;
  }

  if (gameState.gameActive) {
    alert("A game is already in progress. Please finish the current game before starting a new one.");
    return;
  }

  gameState.playerMinTotal = 0; // Reset the running player total
  gameState.bet = bet; // Set the bet amount in the game state
  gameState.gameActive = true // Set the game state to true

  updateUIStats()

  
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



  playerBJ = findBlackjack(playerCard1, playerCard2)
  dealerBJ = findBlackjack(dealerCard1, dealerCard2)
  // Resolve game immediately if someone has a blackjack
  if (playerBJ && dealerBJ) {
    flipDealerCard(dealerFaceDownCard);
    showGameMessage("DOUBLE BLACKJACK! Upping the stakes...", "#FFD64E")
    gameState.gameActive = false
    gameState.multiplier = 2
    gameState.bet = 0
    updateUIStats()
  }

  else if (playerBJ){
    console.log("Player Blackjack!")
    flipDealerCard(dealerFaceDownCard);
    showGameMessage("Blackjack! You Win!", "#4EFF89")

    playerBalance += gameState.multiplier * Math.ceil(1.5 * gameState.bet); // Rounded 3:2 payout for getting blackjack
    endGame()
  }

  else if (dealerBJ){
    console.log("Dealer Blackjack!")
    flipDealerCard(dealerFaceDownCard)
    showGameMessage("Dealer Blackjack!", "#FF4E4E")

    playerBalance -= gameState.multiplier * gameState.bet; // Still lose normal amount apparently
    endGame()
  }
}


// Animations
function showGameMessage(message, color) { 
  const bust = document.getElementById("bust-animation"); // Repurposed the 'bust' animation so all the variables are still called bust - this function is used for all game messages however
  bust.textContent = message;
  bust.style.color = color;

  bust.classList.remove("bust-hidden");
  bust.classList.add("bust-visible");

  setTimeout(() => {
    bust.classList.remove("bust-visible");
    bust.classList.add("bust-hidden");
  }, 1600);
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
