
class Note:
    def __init__(self,note_name,title,summary,video_link,comment_user,comment_user_link,target_user,target_user_link):
        self.note_name = note_name
        self.title = title
        self.summary = summary
        self.video_link = video_link
        self.comment_user = comment_user
        self.comment_user_link = comment_user_link
        self.target_user = target_user
        self.target_user_link = target_user_link
        
    async def create_note(self):
        markdown_content = f"""
# {self.title}

## AI conclusion
```{self.summary}```

## video link
[videolink]({self.video_link})

## source user

- comment_user [@{self.comment_user}]({self.comment_user_link}) 
- target_user [@{self.target_user}]({self.target_user_link})
        
        """
        with open(self.note_name+'.md', 'w') as md_file:
            md_file.write(markdown_content)