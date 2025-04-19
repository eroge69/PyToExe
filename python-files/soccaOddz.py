def main():
    while True:
        # Get user input for the match
        team1 = input("\nEnter home team name (or 'q' to quit): ")
        if team1.lower() == 'q':
            break

        team2 = input("Enter away team name: ")
        if team2.lower() == 'q':
            break

        try:
            home_win = float(input("Enter Odds for home team1: "))  # Fixed variable name and converted to float
            draw = float(input("Enter Odds for a draw: "))  # Fixed variable name and converted to float
            away_win = float(input("Enter Odds for away team2: "))  # Fixed variable name and converted to float
        except ValueError:
            print("Invalid input. Please enter numeric values for odds.")
            continue

        # Create odds dictionary
        odds = {
            'home_win': home_win,
            'draw': draw,
            'away_win': away_win
        }

        # Calculate probabilities
        probabilities = calculate_probabilities(odds)

        # Display results
        display_probabilities(team1, team2, odds, probabilities)

        # Ask if user wants to continue
        cont = input("\nWould you like to analyze another match? (y/n): ")
        if cont.lower() != 'y':
            break


def calculate_probabilities(odds):
    """
    Converts bookmaker odds to implied probabilities
    """
    # Calculate raw implied probability for each outcome
    raw_prob_home = 1 / odds['home_win']
    raw_prob_draw = 1 / odds['draw']
    raw_prob_away = 1 / odds['away_win']

    # Calculate total implied probability (for normalization)
    total_prob = raw_prob_home + raw_prob_draw + raw_prob_away
    overround = total_prob - 1  # Bookmaker's margin

    # Normalize probabilities to sum to 1 (100%)
    probabilities = {
        'raw': {
            'home_win_prob': raw_prob_home,
            'draw_prob': raw_prob_draw,
            'away_win_prob': raw_prob_away,
            'total_prob': total_prob,
            'overround': overround
        },
        'normalized': {
            'home_win_prob': raw_prob_home / total_prob,
            'draw_prob': raw_prob_draw / total_prob,
            'away_win_prob': raw_prob_away / total_prob
        }
    }

    return probabilities


def display_probabilities(team1, team2, odds, probabilities):
    """
    Displays the odds and probabilities in a readable format
    """
    print(f"\nMatch: {team1} vs {team2}")
    print("----------------------------")
    print(f"Odds - {team1} win: {odds['home_win']:.2f}")
    print(f"Odds - Draw: {odds['draw']:.2f}")
    print(f"Odds - {team2} win: {odds['away_win']:.2f}")

    print("\nRaw Implied Probabilities (before normalization):")
    print(f"{team1} win: {probabilities['raw']['home_win_prob'] * 100:.1f}%")
    print(f"Draw: {probabilities['raw']['draw_prob'] * 100:.1f}%")
    print(f"{team2} win: {probabilities['raw']['away_win_prob'] * 100:.1f}%")
    print(f"Total implied probability: {probabilities['raw']['total_prob'] * 100:.1f}%")
    print(f"Bookmaker overround (margin): {probabilities['raw']['overround'] * 100:.1f}%")

    print("\nNormalized Probabilities (after accounting for overround):")
    print(f"{team1} win: {probabilities['normalized']['home_win_prob'] * 100:.1f}%")
    print(f"Draw: {probabilities['normalized']['draw_prob'] * 100:.1f}%")
    print(f"{team2} win: {probabilities['normalized']['away_win_prob'] * 100:.1f}%")


if __name__ == "__main__":
    print("Ronny Sports Betting Odds Analyzer")
    print("----------------------------")
    print("Enter match details to see implied probabilities.")
    print("Enter 'q' at any time to quit.\n")
    main()
    print("\nThank you for using the Ronny Sports Betting Odds Analyzer. Goodbye!")