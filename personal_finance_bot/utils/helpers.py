import re
import matplotlib
matplotlib.use('Agg') # Use a non-interactive backend for generating files without GUI
import matplotlib.pyplot as plt
import csv
import os # For os.path.exists if we add checks for filename, and for removing test files
from datetime import datetime # For testing generate_expenses_csv with datetime objects

def parse_expense_message(message_text: str):
    if not isinstance(message_text, str):
        return None, None

    message_text_stripped = message_text.strip()

    value_regex_str = r"((?:[+-]?\d[\d.,]*\d)|(?:[+-]?\d+))\s*$"
    value_regex = re.compile(value_regex_str)
    match = value_regex.search(message_text_stripped)

    if not match:
        return None, None

    value_str = match.group(1)
    description = message_text_stripped[:match.start()].strip()

    common_currencies = ["R$", "$", "EUR", "€", "£"]
    for currency_symbol in common_currencies:
        if description.endswith(currency_symbol):
            description = description[:-len(currency_symbol)].strip()
            break

    has_dot = '.' in value_str
    has_comma = ',' in value_str

    if has_dot and has_comma:
        if value_str.rfind(',') > value_str.rfind('.'):
            value_str_normalized = value_str.replace('.', '').replace(',', '.')
        elif value_str.rfind('.') > value_str.rfind(','):
            value_str_normalized = value_str.replace(',', '')
        else:
            return None, None
    elif has_comma:
        value_str_normalized = value_str.replace(',', '.')
    elif has_dot:
        value_str_normalized = value_str
    else:
        value_str_normalized = value_str

    try:
        value = float(value_str_normalized)
    except ValueError:
        return None, None

    if not description:
        return None, None

    return description, value

def generate_pie_chart(expenses_by_category: list[tuple[str, float]], filename: str) -> str | None:
    """
    Generates a pie chart from expense data and saves it to a file.
    expenses_by_category: A list of tuples, e.g., [('Food', 50.0), ('Transport', 30.0)].
    filename: The path to save the pie chart image.
    Returns the filename if successful, None otherwise.
    """
    if not expenses_by_category:
        return None

    labels = [item[0] for item in expenses_by_category]
    sizes = [item[1] for item in expenses_by_category]

    fig, ax = plt.subplots(figsize=(10, 7)) # Adjust figure size for better readability
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=None, # Labels will be handled by legend or outside
        autopct='%1.1f%%',
        startangle=90,
        shadow=False,
        pctdistance=0.85 # Distance of percentage text from center
    )
    ax.axis('equal')
    plt.title("Resumo de Despesas por Categoria", pad=20)

    # Add a legend
    ax.legend(wedges, labels, title="Categorias", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    plt.tight_layout()


    try:
        plt.savefig(filename, bbox_inches='tight') # bbox_inches='tight' helps fit legend
        plt.close(fig)
        return filename
    except Exception as e:
        print(f"Error saving pie chart: {e}")
        plt.close(fig)
        return None

def generate_expenses_csv(expenses_data: list[tuple], filename: str) -> str | None:
    """
    Generates a CSV file from a list of expense records.
    expenses_data: List of tuples, where each tuple is a row from the db.
                   Expected format: (id, user_id, value, description, category, timestamp)
    filename: The path to save the CSV file.
    Returns the filename if successful, None otherwise.
    """
    if not expenses_data:
        return None

    header = ['ID da Despesa', 'ID do Usuário', 'Valor', 'Descrição', 'Categoria', 'Data/Hora']

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(header)
            for expense_row in expenses_data:
                row_to_write = list(expense_row)
                if len(row_to_write) > 5: # Timestamp is at index 5
                    ts = row_to_write[5]
                    if isinstance(ts, str):
                        try:
                            # Attempt to parse if it's a common ISO format string from DB
                            dt_obj = datetime.fromisoformat(ts)
                            row_to_write[5] = dt_obj.strftime('%Y-%m-%d %H:%M:%S')
                        except ValueError:
                             # if parsing fails, keep original string representation
                            pass
                    elif isinstance(ts, datetime): # If it's already a datetime object
                        row_to_write[5] = ts.strftime('%Y-%m-%d %H:%M:%S')
                    # If it's neither string nor datetime, keep as is (though less likely for timestamp)
                csv_writer.writerow(row_to_write)
        return filename
    except IOError as e:
        print(f"Error writing CSV file: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during CSV generation: {e}")
        return None

if __name__ == '__main__':
    # Tests for parse_expense_message
    test_cases_parser = [
        ("Picolé 5,95", ("Picolé", 5.95)),
        ("Uber 18", ("Uber", 18.0)),
        ("Aluguel 1200", ("Aluguel", 1200.0)),
        ("  Lanche especial   12.50  ", ("Lanche especial", 12.50)),
        ("Cinema R$30", ("Cinema", 30.0)),
        ("Cinema $25.50", ("Cinema", 25.50)),
        ("Bolo EUR20", ("Bolo", 20.0)),
        ("Café 3.5", ("Café", 3.5)),
        ("Compra mercado 125,70", ("Compra mercado", 125.70)),
        ("Salário +3000", ("Salário", 3000.0)),
        ("Conta de luz - energia 75.99", ("Conta de luz - energia", 75.99)),
        ("Presente £15", ("Presente", 15.0)),
        ("Apenas texto", (None, None)),
        ("123", (None, None)),
        ("R$123", (None, None)),
        ("$50.25", (None, None)),
        ("EUR40", (None, None)),
        ("123 Description after number", (None, None)),
        ("Description with R$ in middle 50", ("Description with R$ in middle", 50.0)),
        ("Item R$ 22,50",("Item", 22.50)),
        ("Item $10", ("Item", 10.0)),
        ("Item EUR 100.00", ("Item", 100.0)),
        ("  ", (None, None)),
        ("", (None, None)),
        ("Texto com valor no meio 10 e depois mais texto", (None, None)),
        ("Supermercado 1.000,50", ("Supermercado", 1000.50)),
        ("Supermercado 1,000.50", ("Supermercado", 1000.50)),
        ("Value 123.456,78", ("Value", 123456.78)),
        ("Value 12,345.67", ("Value", 12345.67)),
        (None, (None, None)),
        (12345, (None, None)),
    ]

    print("Running test cases for parse_expense_message...")
    all_tests_passed_parser = True
    for i, (text, expected) in enumerate(test_cases_parser):
        desc, val = parse_expense_message(text)
        if (desc, val) == expected:
            print(f"PASS ({i+1}/{len(test_cases_parser)}): '{text}' -> ({desc}, {val})")
        else:
            all_tests_passed_parser = False
            print(f"FAIL ({i+1}/{len(test_cases_parser)}): '{text}'")
            print(f"  Expected: {expected}")
            print(f"  Got:      ({desc}, {val})")

    if all_tests_passed_parser:
        print("All parse_expense_message tests passed!")
    else:
        print("Some parse_expense_message tests FAILED!")

    # Tests for generate_pie_chart and generate_expenses_csv
    print("\n--- Testing generate_pie_chart ---")
    sample_pie_data = [('Alimentação', 150.75), ('Transporte', 65.0), ('Lazer', 80.20), ('Outros', 40.0)]
    pie_chart_file = "test_pie_chart.png"
    if generate_pie_chart(sample_pie_data, pie_chart_file):
        print(f"Pie chart generated: {pie_chart_file}. Please verify manually.")
        if os.path.exists(pie_chart_file):
             os.remove(pie_chart_file) # Clean up
    else:
        print("Pie chart generation failed.")

    print("\n--- Testing generate_expenses_csv ---")
    sample_csv_data = [
        (1, 1001, 50.0, "Almoço executivo", "Alimentação", datetime.now()),
        (2, 1001, 12.5, "Café", "Alimentação", "2023-10-25 10:30:00.123456"),
        (3, 1002, 200.0, "Show", "Lazer", datetime(2023, 10, 24, 20, 0, 0)),
        (4, 1001, 75.90, "Gasolina", "Transporte", "2023-10-23 08:15:30")
    ]
    csv_file = "test_expenses.csv"
    if generate_expenses_csv(sample_csv_data, csv_file):
        print(f"CSV file generated: {csv_file}. Please verify content manually.")
        # Verify content (optional, basic check)
        try:
            with open(csv_file, 'r', newline='', encoding='utf-8') as f_check:
                reader = csv.reader(f_check)
                header = next(reader)
                assert header == ['ID da Despesa', 'ID do Usuário', 'Valor', 'Descrição', 'Categoria', 'Data/Hora']
                print("CSV header is correct.")
                data_rows = list(reader)
                assert len(data_rows) == len(sample_csv_data)
                print(f"CSV has {len(data_rows)} data rows, matching input.")
            if os.path.exists(csv_file):
                os.remove(csv_file) # Clean up
        except Exception as e_check:
            print(f"Error verifying CSV content: {e_check}")
    else:
        print("CSV generation failed.")
