from fare_tracker import *

while True:
    print("1. Add train to tracker")
    print("2. Track trains")
    print("3. Exit")
    choice = input("Enter choice: ")
    if choice == "1":
        origin = input("Enter origin station code: ")
        destination = input("Enter destination station code: ")
        date = input("Enter date (DDMMYY): ")
        add_train_to_tracker(origin, destination, date)
    elif choice == "2":
        track_trains()
    elif choice == "3":
        break
    else:
        print("Invalid choice.")