import os

def navigate_directories(starting_path="."):
    """
    Allow the user to navigate directories to select a file.

    Parameters:
        starting_path (str): The initial path to start the navigation.

    Returns:
        str: The selected file path.
    """
    current_path = os.path.abspath(starting_path)

    while True:
        print(f"\nCurrent Directory: {current_path}")
        entries = os.listdir(current_path)

        # Separate directories and files
        directories = [d for d in entries if os.path.isdir(os.path.join(current_path, d))]
        files = [f for f in entries if os.path.isfile(os.path.join(current_path, f))]

        print("\nDirectories:")
        for idx, directory in enumerate(directories, start=1):
            print(f"  {idx}. {directory}")

        print("\nFiles:")
        for idx, file in enumerate(files, start=len(directories) + 1):
            print(f"  {idx}. {file}")

        print("\nOptions:")
        print("  0. Select this directory")
        print("  b. Go back to the parent directory")
        print("  q. Quit")

        choice = input("\nEnter your choice (number/b/q): ").strip().lower()

        if choice == "q":
            print("[INFO] Exiting navigation...")
            return None
        elif choice == "b":
            current_path = os.path.dirname(current_path)
        elif choice == "0":
            print("[INFO] Selected directory.")
            return current_path
        elif choice.isdigit() and 1 <= int(choice) <= len(directories) + len(files):
            index = int(choice) - 1
            if index < len(directories):
                # Navigate into the selected directory
                current_path = os.path.join(current_path, directories[index])
            else:
                # Return the selected file
                selected_file = os.path.join(current_path, files[index - len(directories)])
                print(f"[INFO] Selected file: {selected_file}")
                return selected_file
        else:
            print("[ERROR] Invalid choice. Please try again.")