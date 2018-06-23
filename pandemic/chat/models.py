from django.db import models
from django.contrib.auth.models import User
from game.models import Session
import uuid

class Chat(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    def __str__(self):
        return f"session={self.session!s}"

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name="user_message", on_delete=models.CASCADE)
    text = models.CharField(max_length=512)
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.date_time}] {self.sender.username}: {self.text}"
