import random
def dealCard() -> tuple:
    card = random.randint(1, 13)
    cardValue = card

    if card > 10:
        cardValue = 10

    if card == 1:
        card = 'A'
        cardValue = 11 # Count Ace as 11 by default but -10 from total if it would put the total over 21. (this enables blackjack opportunity)
    elif card == 11:
        card = 'J'
    elif card == 12:
        card = 'Q'
    elif card == 13:
        card = 'K'

    return str(card), cardValue

def getTotal(playerCards:list) -> int:
    value = 0
    for card in playerCards: # Iterate through all player cards and add them 1 by 1, this should handle double aces not counting as 1 twice
        if card in ['J', 'Q', 'K']:
            value += 10
        elif card == 'A':
            value += 11 if value + 11 <= 21 else 1 # Ace can be 1 or 11, pick 11 unless that would put the total over 21

        else:
            value += int(card)

    return value

def deal_dealer(dcard1:str, dcard2:str, playerTotal)-> tuple: # Return each card the dealer got then the result of the game
    dealerCards = [dcard1, dcard2] # Each item in list should be a string of 1 character
    dTotal = getTotal(dealerCards)

    aceCount = 0
    poppedAces = 0 # The aces are like the minecraft totem of undying so we need to count how many of them the dealer popped already to compare with how many he has

    
    while dTotal < playerTotal: # Dealer doesn't stop hitting until his score beats the player -> This is a much harder ruling than normal blackjack good luck playtesters you get 1k moneys anyway
        newCard, dCardValue = dealCard() # newCard is the card to visually generate, dhitcard is the value of the card
        dealerCards.append(newCard)
        print("Dealer got:", newCard)

        if newCard.startswith('A'):
            aceCount += 1 # Count how many aces the dealer has

        dTotal += dCardValue

        if dTotal >= 22:

            if poppedAces < dealerCards.count('A'): # If the dealer had an Ace, subtract 10 from the total to change its value to 1
                poppedAces += 1
                dTotal -= 10

                print("Dealer's total is over 21, Ace changed to 1")
                print(f"Dealer's new total: {dTotal}")
            
            else:
                print()
                print("Dealer Busts")
                
                return dealerCards, "Dealer Busts"


        print(f"Dealer's total: {dTotal}")

    if dTotal == playerTotal:
        print("Tie")
        return dealerCards, "Push"
    elif dTotal < playerTotal:
        print("Player wins")
        return dealerCards, "Player Wins"
    
    elif dTotal > playerTotal:
        print("Dealer Wins")
        return dealerCards, "Dealer Wins"

    else:
        print("No one wins?")
        print("dTotal:", dTotal)
        print("PlayerTotal:", playerTotal)
        

            
            