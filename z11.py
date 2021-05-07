with open("z1.txt", 'r') as input_file:
    file_contents = input_file.read()

    def char_remove(file_contents):
        char = [",", ".", ":", ";", "!", "?"]
        for i in file_contents.lower():
            if i in char:
                file_contents = file_contents.replace(i, "")
        return file_contents
    print(char_remove(file_contents))
    word_list = file_contents.split()
    word_count = {word: word_list.count(word) for word in word_list}
    print(word_count)
    print('Największa ilość wystąpień:')
    x = sorted(word_count.items(), key=lambda o: o[1], reverse=True)[:5]
    for k,o in reversed(x):
        print(str(k)+": "+str(o))

    print('Lączna licba slow w tekscie: ', len(word_list))
