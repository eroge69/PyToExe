def factorial(n):
    """
    Calculates the factorial of a non-negative integer.  You know, like, n!

    Args:
        n: A non-negative integer.  Duh.

    Returns:
        The factorial of n.  It's what you get when you multiply all the numbers
        from 1 to n.  Returns 1 if n is 0, because...reasons.
        Raises ValueError if n is negative.  Don't give me negative numbers,
        I'm not a magician.  Raises TypeError if it is not an integer. Are you kidding me?
    """
    if not isinstance(n, int):
        raise TypeError("Input must be an integer.  Are you trying to break me?")
    if n < 0:
        raise ValueError("Input must be a non-negative integer.  No negatives allowed, pal.")
    if n == 0:
        return 1  # Because 0! is 1.  Don't ask me why.
    else:
        result = 1
        for i in range(1, n + 1):
            result *= i  # Multiply, multiply, multiply!
        return result

# Example usage
try:
    num = 5
    fact = factorial(num)
    print(f"The factorial of {num} is {fact}.  That's {fact}, for you mathletes.")  # Output: The factorial of 5 is 120

    num = 0
    fact = factorial(num)
    print(f"The factorial of {num} is {fact}.  Even zero has a factorial, who knew?")  # Output: The factorial of 0 is 1

    num = -1
    fact = factorial(num) # This will raise a ValueError
    print(f"The factorial of {num} is {fact}")

    num = 2.5
    fact = factorial(num) # This will raise a TypeError
    print(f"The factorial of {num} is {fact}")

except ValueError as e:
    print(f"Error: {e}.  What part of 'non-negative' did you not understand?")  # Output: Error: Input must be a non-negative integer.
except TypeError as e:
    print(f"Error: {e}. Seriously? An Integer. Not a float, not a string, an INTEGER!") # Output: Error: Input must be an integer.
