from flask import Flask, render_template, request
from datetime import datetime
from json import dumps, loads
from json.decoder import JSONDecodeError

app = Flask(__name__)


def give_operation_date():
    present_date = datetime.now()
    return present_date.strftime("%d-%m-%Y %H:%M:%S")


@app.route("/", methods=["GET", "POST"])
def index():
    amount_in_account = 0  # Stan konta
    warehouse = {}  # Słownik - magazyn
    operation_history = []

    # Odczytanie danych z plików
    try:
        with open("data_amount_in_account.txt") as file_stream:
            amount_txt_data = file_stream.readline()

            if amount_txt_data:
                amount_in_account = amount_txt_data
    except FileNotFoundError:
        print("Nie pobrano danych z pliku.")

    try:
        with open("warehouse.json") as file_stream:
            warehouse_txt_data = file_stream.read()

            if not warehouse_txt_data:
                print("Plik jest pusty.")
            else:
                warehouse = loads(warehouse_txt_data)
    except FileNotFoundError:
        print("Nie pobrano danych z pliku.")
    except JSONDecodeError as e:
        print(f"Wystąpił nieoczekiwany błąd {e}.")

    try:
        with open("operation_history.json") as file_stream:
            operation_history_txt_data = file_stream.read()

            if not operation_history_txt_data:
                pass
                print("Plik jest pusty.")
            else:
                operation_history = loads(operation_history_txt_data)
    except FileNotFoundError:
        print("Nie pobrano danych z pliku.")
    except JSONDecodeError as e:
        print(f"Wystąpił nieoczekiwany błąd {e}.")

    amount_in_account = int(amount_in_account)

    # Dodanie lub odjęcie wartości od kwoty na koncie
    difference_in_account = request.form.get("difference_in_account")

    if difference_in_account:
        difference_in_account = int(difference_in_account)
        amount_in_account += difference_in_account

        # Aktualizacja historii operacji - Saldo
        operation_history.append({"Nazwa operacji": "Saldo",
                                  "Opis operacji":
                                      (
                                          f"Kwota operacji: {difference_in_account}\n"
                                          f"Stan konta po operacji: {amount_in_account}"
                                      ),
                                  "Data operacji": give_operation_date()})

    # Zakup produktu
    product_to_buy_name = request.form.get("product_to_buy_name")
    product_to_buy_price = request.form.get("product_to_buy_price")
    product_to_buy_amount = request.form.get("product_to_buy_amount")

    if product_to_buy_name and product_to_buy_price and product_to_buy_amount:
        product_to_buy_price = int(product_to_buy_price)
        product_to_buy_amount = int(product_to_buy_amount)

        amount_in_account = amount_in_account - (product_to_buy_price * product_to_buy_amount)

        #  Sprawdzenie czy dany produkt jest już w magazynie.
        #  Jeśli tak, zwiększenie jego ilości i zamiana ceny
        if product_to_buy_name in warehouse:
            warehouse[product_to_buy_name]["amount"] = warehouse[product_to_buy_name]["amount"] \
                                                       + product_to_buy_amount
            warehouse[product_to_buy_name]["price"] = product_to_buy_price
        else:
            # Dodanie produktu do słownika magazynu
            warehouse[product_to_buy_name] = {
                "price": product_to_buy_price,
                "amount": product_to_buy_amount
            }

        # Aktualizacja historii operacji
        operation_history.append({"Nazwa operacji": "Zakup",
                                  "Opis operacji":
                                      (
                                          f"Nazwa zakupionego produktu: {product_to_buy_name}\n"
                                          f"Kwota zakupu za jeden produkt: {product_to_buy_price}\n"
                                          f"Ilość zakupionych produktów: {product_to_buy_amount}\n"
                                          f"Stan konta po operacji: {amount_in_account}"
                                      ),
                                  "Data operacji": give_operation_date()})

    # Sprzedaż produktu
    product_to_sell_name = request.form.get("product_to_sell_name")
    product_to_sell_price = request.form.get("product_to_sell_price")
    product_to_sell_amount = request.form.get("product_to_sell_amount")

    if product_to_sell_name and product_to_sell_price and product_to_sell_amount:
        product_to_sell_price = int(product_to_sell_price)
        product_to_sell_amount = int(product_to_sell_amount)

        # Odjęcie z magazynu sprzedawanej ilości towaru
        warehouse[product_to_sell_name]["amount"] = \
            warehouse[product_to_sell_name]["amount"] - product_to_sell_amount

        # Sprawdzenie czy jest wystarczająca ilość towaru w magazynie
        if warehouse[product_to_sell_name]["amount"] < 0:
            product_to_sell_amount = product_to_sell_amount + warehouse[product_to_sell_name]["amount"]
            print(f"Brak wystarczającej ilości danego towaru w magazynie. "
                  f"Sprzedano {product_to_sell_amount} sztuk.")
            warehouse[product_to_sell_name]["amount"] = 0

        # Dodanie do konta kwoty sprzedaży
        amount_in_account = amount_in_account + (product_to_sell_price * product_to_sell_amount)

        # Jeśli ilość danego towaru = 0 usunięcie towaru z kartoteki magazynu
        if warehouse[product_to_sell_name]["amount"] == 0:
            del warehouse[product_to_sell_name]

        # Aktualizacja historii operacji
        operation_history.append({"Nazwa operacji": "Sprzedaż",
                                  "Opis operacji":
                                      (
                                          f"Nazwa sprzedanego produktu: {product_to_sell_name}\n"
                                          f"Kwota sprzedaży za jeden produkt: {product_to_sell_price}\n"
                                          f"Ilość sprzedanych produktów: {product_to_sell_amount}\n"
                                          f"Stan konta po operacji: {amount_in_account}"
                                      ),
                                  "Data operacji": give_operation_date()})

    # Zapisanie danych do plików
    with open("data_amount_in_account.txt", "w") as file_stream:
        file_stream.write(str(amount_in_account))

    with open("warehouse.json", "w") as file_stream:
        file_stream.write(dumps(warehouse))

    with open("operation_history.json", "w") as file_stream:
        file_stream.write(dumps(operation_history))

    print("Poprawnie zapisano dane.")




    # elif menu_command in ["5", "lista"]:
    #     # Wyświetla całkowity stan magazynu
    #     print("Stan magazynu: ")
    #     for index, name in enumerate(warehouse):
    #         print(f"{index + 1}. {name.capitalize()}:\n"
    #               f"  cena: {warehouse[name]['price']}\n"
    #               f"  ilość: {warehouse[name]['amount']}")
    #
    # elif menu_command in ["7", "przegląd"]:
    #     # Pobiera zakres wyświetlenia od użytkownika
    #     print(f"Odnotowano {len(operation_history)} operacji w historii.")
    #
    #     if len(operation_history) == 0:
    #         break
    #
    #     display_history_start_number = input("Podaj początkowy indeks historii operacji: ")
    #     if display_history_start_number == "":
    #         display_history_start_number = 1
    #     try:
    #         display_history_start_number = int(display_history_start_number)
    #     except ValueError:
    #         print("Błąd - Należy podać liczbę.")
    #         continue
    #     if display_history_start_number < 1 or display_history_start_number > len(operation_history):
    #         print(
    #             f"Wybrano wartość spoza zakresu. Należy wpisać wartość z przedziału od 1 do {len(operation_history)}")
    #         continue
    #
    #     display_history_end_number = input("Podaj końcowy indeks historii operacji: ")
    #     if display_history_end_number == "":
    #         display_history_end_number = len(operation_history)
    #     try:
    #         display_history_end_number = int(display_history_end_number)
    #     except ValueError:
    #         print("Błąd - Należy podać liczbę.")
    #         continue
    #     if display_history_end_number < 1 or display_history_end_number > len(operation_history):
    #         print(
    #             f"Wybrano wartość spoza zakresu. Należy wpisać wartość z przedziału od 1 do {len(operation_history)}")
    #         continue
    #
    #     # Wyświetla historię operacji
    #     print("Historia operacji:")
    #     for index, operation in enumerate(operation_history):
    #         if index in range(display_history_start_number - 1, display_history_end_number):
    #             indent_date_width = 60 - len(operation["Nazwa operacji"])
    #             justify_operation_date = str(operation["Data operacji"].rjust(indent_date_width))
    #             print(f'{index + 1}. {operation["Nazwa operacji"]} {justify_operation_date}\n'
    #                   f'{operation["Opis operacji"]}')
    #
    return render_template("index.html", amount_in_account=amount_in_account)


@app.route("/historia/")
def history():
    return render_template("history.html")
