# This is a sample Python script.

import typing as tp


def parse_args(args: tp.List[str]) -> tp.Dict[str, str]:
    result = {}
    for arg in args:
        user_input = input("Please provide " + arg + ": ")
        # TODO: Add validation of user input
        result[arg] = user_input
    return result


def read_commands():
    user_input = input("Enter your command (type 'exit' to quit): ")

    # Check if the user wants to exit
    if user_input.lower() == 'exit':
        print("Exiting the program.")
        exit()
    elif user_input.lower() == 'record_receipt':
        print(parse_args(["customer_sample_name", "tube_barcode"]))
    elif user_input.lower() == 'add_to_plate':
        print(parse_args(["sample_one.id", "plate_barcode", "well_position"]))
    elif user_input.lower() == 'tube_transfer':
        print(parse_args(["source_tube_barcode", "destination_tube_barcode"]))
    elif user_input.lower() == 'list_samples_in':
        print(parse_args(["container_barcode"]))


def main():
    while True:
        read_commands()


if __name__ == "__main__":
    main()
