# simple_script.py

result = 4 + 5  # Calculation
output_file = "output.txt"  # Output file name

# Write the result to a file in the same directory
with open(output_file, "w") as file:
    file.write(f"Result: {result}\n")

print(f"Result saved in {output_file}")
