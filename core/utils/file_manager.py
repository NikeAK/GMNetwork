
class FileManager:
    @staticmethod
    def read_file(path: str) -> list:
        with open(path, 'r') as file:
            return [line.strip() for line in file.readlines() if line.strip()]

    @staticmethod
    def save_str_file(path: str, string: str):
        with open(path, 'a') as file:
            file.writelines(string + '\n')

    @staticmethod
    def delete_str_file(path: str, string: str) -> None:
        with open(path, 'r') as file:
            string = string[7:] if string.startswith('http://') else string
            lines = [line.strip() for line in file.readlines() if line.strip() and string not in line]
        with open(path, 'w') as file:
            file.write('\n'.join(lines))
            
    @staticmethod
    def save_data(path: str, data: str):
        with open(path, 'w') as file:
            file.write(data)

