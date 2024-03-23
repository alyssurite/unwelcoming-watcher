"""Database types"""

from bot.db.models import Group, User

GroupID = Group | int
UserID = User | int
