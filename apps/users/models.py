from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CharField,
    IntegerField,
    BooleanField,
    DateTimeField,
    ForeignKey,
    URLField,
    TextField,
    OneToOneField,
    ManyToManyField,
    CASCADE,
)
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from model_utils.models import TimeStampedModel, StatusModel, TimeFramedModel
from model_utils import Choices

from apps.tokens.models import Tokens
from utils.custom_fields import ListField


class BannedWords(TimeStampedModel):
    chat_id = CharField(_("Group ID"), max_length=15, blank=False, unique=True, null=True)
    words = ListField()

    def __str__(self):
        return f"Banned Words for {self.chat_id}"

class LinksException(TimeStampedModel):
    chat_id = CharField(_("Group ID"), max_length=15, blank=False, unique=True, null=True)
    links = ListField()

    def __str__(self):
        return f"Exceptional Links {self.chat_id}"

class TelegramGroup(TimeStampedModel):
    chat_id = CharField(_("Group ID"), max_length=15, blank=False, unique=True, null=True)
    group_name = CharField(_("Group Name"), max_length=255, blank=False, unique=True, null=True)
    subscribed = BooleanField(default=False)

    about = TextField(blank=True, null=True)
    welcome_message = TextField(blank=True, null=True)
    goodbye_message = TextField(blank=True, null=True)
    website = URLField(null=True)
    support = URLField(null=True)

    max_warnings = IntegerField(default=3)
    mute_duration = IntegerField(default=1) # in minutes
    ban_duration = IntegerField(default=7) # in days
    max_message_length = IntegerField(default=300)
    delete_messages = BooleanField(default=True)


    but_token_link = URLField(null=True)
    buy_token_name = ForeignKey(Tokens, on_delete=CASCADE, null=True, related_name="buy_token_name")

    allow_links = BooleanField(default=False)
    must_have_username = BooleanField(default=True)
    must_have_about = BooleanField(default=True)
    must_have_description = BooleanField(default=True)

    block_porn = BooleanField(default=True)
    allow_hash = BooleanField(default=False)
    allow_mention = BooleanField(default=False)
    enable_captcha = BooleanField(default=False)
    unverified_user_duration = IntegerField(default=7)
    watch_for_spam = BooleanField(default=False)
    watch_length = BooleanField(default=True)
    prevent_flooding = BooleanField(default=False)

    offenders = ListField()

    def __str__(self):
        return str(self.chat_id)

class TelegramGroupCaptcha(TimeStampedModel):
    group_id = CharField(max_length=15, blank=True, null=True)
    user_id = IntegerField(unique=True)
    captcha_code = IntegerField(unique= True)
    expires = DateTimeField(null=True)
    used = BooleanField(default=False)

    def __str__(self) -> str:
        return str(self.group.chat_id)

class TelegramGroupFlooding(TimeStampedModel):
    group = OneToOneField(TelegramGroup, on_delete=CASCADE, related_name="flood_settings")
    messages_before_block = IntegerField(default=5) # messages
    repeats_timeframe = IntegerField(default=3) # seconds
    ban = BooleanField(default=True)
    kick = BooleanField(default=False)
    mute = BooleanField(default=False)

    def __str__(self) -> str:
        return str(self.group.chat_id)

class TelegramGroupMediaActions(TimeStampedModel):
    """
    0 - Allow
    1 - Warn
    2 - Delete
    3 - Ban the user
    4 - Warn before ban
    """
    group = OneToOneField(TelegramGroup, on_delete=CASCADE, related_name="media_actions")
    images = IntegerField(default=0)
    videos = IntegerField(default=0)
    animation = IntegerField(default=0)
    audio = IntegerField(default=0)
    sticker = IntegerField(default=0)
    documents = IntegerField(default=0)

    def __str__(self) -> str:
        return str(self.group.chat_id)


class GroupPinnedMessages(TimeStampedModel):
    group = ForeignKey(TelegramGroup, on_delete=CASCADE, related_name="pinned_group")
    pinned_message_id = IntegerField(unique=True)
    pinned_message_text = TextField()

    def __str__(self):
        return f"{self.group.group_name} Pinned Messages"

class GroupOffenders(TimeStampedModel):
    group = ForeignKey(TelegramGroup, on_delete=CASCADE, related_name="offender_group")
    user_id = CharField(_("User ID"), max_length=15, blank=False, unique=True, null=True)
    warned_times = IntegerField(default=3)
    start_date = DateTimeField(auto_now_add=True, null=True)
    end_date = DateTimeField(auto_now_add=False, null=True)

    def __str__(self):
        return f"{self.user_id} in {self.group.group_name} penalized until {self.end_date}"

class GroupAdmins(TimeStampedModel):
    MODERATOR = 'MODERATOR'
    ENFORCER = 'ENFORCER'
    SUPERADMIN = 'SUPERADMIN'
    SUPPORT = 'SUPPORT'
    ROLES = (
        (MODERATOR, MODERATOR),
        (ENFORCER, ENFORCER),
        (SUPERADMIN, SUPERADMIN),
        (SUPPORT, SUPPORT),
    )
    group = ForeignKey(TelegramGroup, on_delete=CASCADE, related_name="admin_group")
    user_id = CharField(_("User ID"), max_length=15, blank=False, unique=True, null=True)
    role = CharField(max_length=25, choices=ROLES, default=SUPERADMIN)

    def __str__(self):
        return f"{self.user_id} in {self.group.group_name} hold administrative role as {self.role.title()}"


class User(AbstractUser):
    """
    Default custom user model for ezziee.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    chat_id = CharField(_("Chat ID"), max_length=15, blank=False, unique=True, null=True)
    user_id = CharField(_("User ID"), max_length=15, blank=False, unique=True, null=True)
    subscribed = BooleanField(_("Subscribed"), default=False)
    violated = BooleanField(_("Violated"), default=False)
    chosen_language = CharField(_("Chosen Language"), max_length=20, default="English")
    groups = ManyToManyField(TelegramGroup, related_name='groups')

    first_name = None  # type: ignore
    last_name = None  # type: ignore

    def __str__(self):
        return str(self.chat_id)
