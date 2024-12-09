import csv

def clean_number(val):
    # Convert string to float if possible and remove unnecessary decimals
    try:
        numeric_val = float(val)
        # Convert integer floats to int
        if numeric_val.is_integer():
            return str(int(numeric_val))
        else:
            return str(numeric_val)
    except ValueError:
        # If not a number, just return val as is
        return val

with open("design_results_250.csv", "r", newline="") as infile:
    reader = csv.DictReader(infile)

    # Initialize a counter starting at 1
    row_counter = 1

    for row in reader:
        # Get values from CSV using the column headers
        f_max_str = row["Max Radius"]    # originally f_max
        r_min_1_str = row["Pulley Sum"]  # originally r_min_1
        r_min_2_str = row["Linkage Sum"] # originally r_min_2
        # r_min_3 is a constant "5"
        r_min_3_str = "5"

        # Convert and clean up values
        f_max_val = round(float(f_max_str))
        r_min_1_val = clean_number(r_min_1_str)
        r_min_2_val = clean_number(r_min_2_str)
        r_min_3_val = r_min_3_str

        # Use the row_counter as the "model number"
        model_number = row_counter

        # Print in the desired format:
        # Example: "816 <- model 1 -> 37.5, 400, 5"
        print(f"{f_max_val} ↤ model {model_number} ↦ {r_min_1_val} mm, {r_min_2_val} mm, {r_min_3_val}")

        # Increment the counter for the next row
        row_counter += 1
