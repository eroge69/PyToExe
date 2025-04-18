def main():
    # Get user input for the match
    team1 = input("Enter home team name: ")
    team2 = input("Enter away team name: ")
    home_win = float(input("Enter Odds for home team1: "))  # Fixed variable name and converted to float
    draw = float(input("Enter Odds for a draw: "))  # Fixed variable name and converted to float
    away_win = float(input("Enter Odds for away team2: "))  # Fixed variable name and converted to float

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


def calculate_probabilities(odds):
    """
    Converts bookmaker odds to implied probabilities
    """
    # Calculate implied probability for each outcome
    prob_home = 1 / odds['home_win']
    prob_draw = 1 / odds['draw']
    prob_away = 1 / odds['away_win']

    # Calculate total implied probability (for normalization)
    total_prob = prob_home + prob_draw + prob_away

    # Normalize probabilities to sum to 1 (100%)
    probabilities = {
        'home_win_prob': prob_home / total_prob,
        'draw_prob': prob_draw / total_prob,
        'away_win_prob': prob_away / total_prob
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
    print("\nImplied Probabilities:")
    print(f"{team1} win: {probabilities['home_win_prob'] * 100:.1f}%")
    print(f"Draw: {probabilities['draw_prob'] * 100:.1f}%")
    print(f"{team2} win: {probabilities['away_win_prob'] * 100:.1f}%")


if __name__ == "__main__":
    main()