import random

# Función para calcular el conteo Hi-Lo
def update_count(hand):
    count = 0
    for card in hand:
        if card in ['2', '3', '4', '5', '6']:
            count += 1
        elif card in ['10', 'J', 'Q', 'K', 'A']:
            count -= 1
    return count

# Función para calcular el conteo verdadero (True Count)
def true_count(count, remaining_decks):
    return count / remaining_decks

# Función para determinar cuánto apostar
def calculate_bet(bankroll, count, minimum_bet):
    if count >= 2:
        return round(bankroll * 0.30)  # Apuesta fuerte
    elif count == 1:
        return round(bankroll * 0.20)  # Apuesta moderada
    elif count <= 0:
        return minimum_bet  # Apostar lo mínimo

def main():
    print("Bienvenido a la app de apuestas de Blackjack.")

    # Input de la banca inicial y apuesta mínima
    bankroll = float(input("Ingresa tu saldo inicial: $"))
    minimum_bet = float(input("Ingresa la apuesta mínima de la mesa: $"))
    
    # Simulamos las cartas del mazo
    deck = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 8  # Mazo de 8 barajas
    random.shuffle(deck)
    
    # Definir el número de barajas restantes
    remaining_decks = len(deck) / 52
    hand = random.sample(deck, 2)  # Tomamos 2 cartas al azar para la mano inicial
    deck = [card for card in deck if card not in hand]  # Eliminar cartas jugadas

    # Calcular el conteo de cartas
    count = update_count(hand)
    print(f"Mano actual: {hand}")
    print(f"Conteo de cartas: {count}")
    
    # Calcular el conteo verdadero (True Count)
    true_count_value = true_count(count, remaining_decks)
    print(f"Conteo verdadero: {true_count_value:.2f}")
    
    # Calcular cuánto apostar
    bet = calculate_bet(bankroll, count, minimum_bet)
    print(f"💰 Apostar: ${bet}")

    # Opcional: Simulación de cambio de mazo (cuando se reinicia el conteo)
    if len(deck) < 20:
        print("🔄 Cambio de mazo detectado. Esperando más cartas para estabilizar el conteo.")
        # Después de un cambio de mazo, apostamos lo mínimo hasta estabilizar
        bet = minimum_bet
        print(f"💰 Apostar (después del cambio de mazo): ${bet}")

    # Mostrar la apuesta final
    print(f"\nTu apuesta final para esta mano es: ${bet}")

if __name__ == "__main__":
    main()
