from fare_tracker import *
import discordbot as dis

while True:
    print("1. Add train to tracker")
    print("2. Remove train from tracker")
    print("3. Add subscribed user")
    print("4. Remove subscribed user")
    print("5. Track trains")
    print("6. Exit")
    choice = input("Enter choice: ")
    match choice:
        case "1":
            origin = input("Enter origin station code: ")
            destination = input("Enter destination station code: ")
            date = input("Enter date (DDMMYY): ")
            add_train_to_tracker(origin, destination, date)
        case "2":
            for i, train in enumerate(get_tracked_trains()):
                print(f"{i}. {train}")
            index = int(input("Enter index of train to remove: "))
            remove_train_from_tracker(index)
        case "3":
            user_id = input("Enter user id: ")
            dis.subscribe_user(int(user_id))
        case "4":
            for i, user in enumerate(dis.get_subscribed_users()):
                print(f"{i}. {user}")
            index = int(input("Enter index of user to remove: "))
            dis.remove_subscribed_user(index)
        case "5":
            dis.run_client()
        case "6":
            exit()
        case default:
            print("Invalid choice.")
            continue
