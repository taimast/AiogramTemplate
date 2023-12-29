import os

def merge_files(root_dir, output_file):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for subdir, dirs, files in os.walk(root_dir):
            for file in files:
                file:str
                if file.endswith(('.py', '.yml', 'ignore', '.yaml')):
                    file_path = os.path.join(subdir, file)
                    outfile.write(f"\n\n--- File Path: {file_path} ---\n\n")
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())

# Использование функции
root_directory = r'G:\CodeProjects\PycharmProjects\AiogramProjectTemplate\project'  # Замените на путь к вашей директории
output_file_path = 'merged_files.txt'      # Название итогового файла
merge_files(root_directory, output_file_path)
