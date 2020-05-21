from src import BD


word_list = ["无人机"]
for word in word_list:
    down = BD(word)
    down.start()