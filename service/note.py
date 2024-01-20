title = "Your Title"
intro = "Your Intro"
link = "Your Link"
user_name = "Your User ID"
user_link = "Your User Link"

markdown_content = f"""
# {title}
##{intro}
[link]({link})
[@{user_name}]({user_link})
"""

# 使用 'w' 参数是为了确保如果文件不存在就创建新的，
# 如果文件已经存在就覆盖原有内容
with open('your_file.md', 'w') as md_file:
    md_file.write(markdown_content)