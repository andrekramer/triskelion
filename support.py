
def read_file_as_string(filepath):
    try:
        with open(filepath, 'r') as file:
            file_content = file.read()
        return file_content
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading '{filepath}': {e}")
        return None