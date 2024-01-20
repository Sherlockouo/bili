def cut_message(msg):
    chat_str = ''.join(msg)
    return [chat_str[i:i+300] for i in range(0, len(chat_str), 300)]