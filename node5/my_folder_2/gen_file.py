# Let's generate a 512 KB text file
# Each KB is 1024 bytes, so 512 KB will be 512 * 1024 bytes

file_size_kb = 512
file_size_bytes = file_size_kb * 1024
text_content = "naruto naruto naruto double sakura sakura sakura triple sasuke sasuke sasuke penta c" * (file_size_bytes // len("This is a sample text. "))

# Write this content to a text file
file_path = 'naruto.txt'
with open(file_path, 'w') as f:
    f.write(text_content)

file_path