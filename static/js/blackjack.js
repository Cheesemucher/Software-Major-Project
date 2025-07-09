
// Helpers for functionality of the actual blackjack game
function drawCard() {
  const card = Math.floor(Math.random() * 13) + 1;
  return card === 1 ? 11 : Math.min(card, 10);
}

function drawInitialHand() {
  const card1 = drawCard();
  const card2 = drawCard();
  const value = card1 + card2;
  return {
    cards: [card1, card2],
    value: value
  };
}

function simulateDealer(playerValue) {
  let { cards, value } = drawInitialHand();

  while (value < playerValue && value < 22) {
    let card = drawCard();
    cards.push(card);
    value += card;

    // Ace adjustment
    if (value > 21 && cards.includes(11)) {
      const aceIndex = cards.indexOf(11);
      cards[aceIndex] = 1;
      value -= 10;
    }
  }

  return { cards, value };
}

// Main function to play a round of blackjack

function playBlackjackRound() {
  const player = drawInitialHand();
  const dealer = simulateDealer(player.value);

  let result = "undecided";
  if (player.value === 21) result = "blackjack";
  else if (player.value > 21) result = "bust";
  else if (dealer.value > 21) result = "dealer_bust";
  else if (dealer.value === 21) result = "dealer_blackjack";
  else if (dealer.value > player.value) result = "dealer_wins";
  else if (player.value > dealer.value) result = "player_wins";
  else result = "draw";

  return {
    player_cards: player.cards,
    player_total: player.value,
    dealer_cards: dealer.cards,
    dealer_total: dealer.value,
    result: result
  };
}

let currentPlayer = {
  cards: [],
  total: 0
};

function startNewRound() {
  const game = playBlackjackRound();

  // Save result to state if needed
  currentPlayer = {
    cards: game.player_cards,
    total: game.player_total
  };

  document.querySelector(".bj-card-box").innerText = `You: ${game.player_cards.join(", ")} (Total: ${game.player_total})`;
  document.querySelector(".bj-text-block").innerText = `Dealer: ${game.dealer_cards.join(", ")} (Total: ${game.dealer_total})`;

  alert("Result: " + game.result);
}

function hit() {
  // Real-time HIT action can be added here later
  alert("Use STAND to see the final result.");
}

function stand() {
  startNewRound();
}

