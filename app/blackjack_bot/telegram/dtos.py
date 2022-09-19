from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, conbytes, constr

from .constants import MessageEntityType


class TelegramResponse(BaseModel):
    class ResponseParameters:
        migrate_to_chat_id: int | None = None
        retry_after: int | None = None

    ok: bool
    result: Any | None = None
    description: str | None = None
    error_code: int | None = None
    parameters: ResponseParameters | None = None


class User(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None
    is_premium: Literal[True] | None = None
    added_to_attachment_menu: Literal[True] | None = None
    can_join_groups: bool | None = None
    can_read_all_group_messages: bool | None = None
    supports_inline_queries: bool | None = None

    @property
    def short_name(self) -> str:
        if self.last_name:
            return f'{self.first_name} {self.last_name[:1]}'
        return self.first_name


class Chat(BaseModel):
    id: int
    type: Literal['private', 'group', 'supergroup', 'channel']
    title: str | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    # photo: ChatPhoto | None = None
    bio: str | None = None
    has_private_forwards: Literal[True] | None = None
    has_restricted_voice_and_video_messages: Literal[True] | None = None
    join_to_send_messages: Literal[True] | None = None
    join_by_request: Literal[True] | None = None
    description: str | None = None
    invite_link: str | None = None
    pinned_message: Message | None = None
    # permissions: ChatPermissions | None = None
    slow_mode_delay: int | None = None
    message_auto_delete_time: int | None = None
    has_protected_content: Literal[True] | None = None
    sticker_set_name: str | None = None
    can_set_sticker_set: Literal[True] | None = None
    linked_chat_id: int | None = None
    # location: ChatLocation | None = None


class MessageEntity(BaseModel):
    type: MessageEntityType
    offset: int
    length: int
    url: str | None = None  # 'text_link' only
    user: User | None = None  # 'text_mention' only
    language: str | None = None  # 'pre' only
    custom_emoji_id: str | None = None  # 'custom_emoji' only


class InlineKeyboardButton(BaseModel):
    text: str
    url: str | None = None
    callback_data: Annotated[str | None, conbytes(min_length=1, max_length=64)] = None
    # web_app: WebAppInfo | None = None
    # login_url: LoginUrl | None = None
    switch_inline_query: str | None = None
    switch_inline_query_current_chat: str | None = None
    # callback_game: CallbackGame | None = None
    # pay: bool | None = None


class InlineKeyboardMarkup(BaseModel):
    inline_keyboard: list[list[InlineKeyboardButton]]


class SendMessageRequest(BaseModel):
    chat_id: int | str
    text: Annotated[str, constr(min_length=1, max_length=4096)]
    parse_mode: str | None = None
    entities: list[MessageEntity] | None = None
    disable_web_page_preview: bool | None = None
    disable_notification: bool | None = None
    protect_content: bool | None = None
    reply_to_message_id: int | None = None
    allow_sending_without_reply: bool | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    # | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply


class EditMessageTextRequest(BaseModel):
    text: Annotated[str, constr(min_length=1, max_length=4096)]
    chat_id: int | str | None = None
    message_id: int | None = None
    inline_message_id: str | None = None
    parse_mode: str | None = None
    entities: list[MessageEntity] | None = None
    disable_web_page_preview: bool | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    # | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply


class AnswerCallbackQueryRequest(BaseModel):
    callback_query_id: str
    text: str | None = None
    show_alert: bool | None = None
    url: str | None = None
    cache_time: int | None = None


class Message(BaseModel):
    message_id: int
    from_: User | None = Field(None, alias='from')
    sender_chat: Chat | None = None
    date: int
    chat: Chat
    forward_from: User | None = None
    forward_from_chat: Chat | None = None
    forward_from_message_id: int | None = None
    forward_signature: str | None = None
    forward_sender_name: str | None = None
    forward_date: int | None = None
    is_automatic_forward: Literal[True] | None = None
    reply_to_message: Message | None = None
    via_bot: User | None = None
    edit_date: int | None = None
    has_protected_content: Literal[True] | None = None
    media_group_id: str | None = None
    author_signature: str | None = None
    text: str | None = None
    entities: list[MessageEntity] | None = None
    # animation: Animation | None = None
    # audio: Audio | None = None
    # document: Document | None = None
    # photo: list[PhotoSize] | None = None
    # sticker: Sticker | None = None
    # video: Video | None = None
    # video_note: VideoNote | None = None
    # voice: Voice | None = None
    # caption: str | None = None
    # caption_entities: list[MessageEntity] | None = None
    # contact: Contact | None = None
    # dice: Dice | None = None
    # game: Game | None = None
    # poll: Poll | None = None
    # venue: Venue | None = None
    # location: Location | None = None
    new_chat_members: list[User] | None = None
    left_chat_member: User | None = None
    new_chat_title: str | None = None
    # new_chat_photo: list[PhotoSize] | None = None
    # delete_chat_photo: Literal[True] | None = None
    # group_chat_created: Literal[True] | None = None
    # supergroup_chat_created: Literal[True] | None = None
    # channel_chat_created: Literal[True] | None = None
    # message_auto_delete_timer_changed: MessageAutoDeleteTimerChanged | None = None
    # migrate_to_chat_id: int | None = None
    # migrate_from_chat_id: int | None = None
    # pinned_message: Message | None = None
    # invoice: Invoice | None = None
    # successful_payment: SuccessfulPayment | None = None
    # connected_website: str | None = None
    # passport_data: PassportData | None = None
    # proximity_alert_triggered: ProximityAlertTriggered | None = None
    # video_chat_scheduled: VideoChatScheduled | None = None
    # video_chat_started: VideoChatStarted | None = None
    # video_chat_ended: VideoChatEnded | None = None
    # video_chat_participants_invited: VideoChatParticipantsInvited | None = None
    # web_app_data: WebAppData | None = None
    reply_markup: InlineKeyboardMarkup | None = None


class CallbackQuery(BaseModel):
    id: str
    from_: User = Field(..., alias='from')
    message: Message | None = None
    inline_message_id: str | None = None
    chat_instance: str
    data: str | None = None
    game_short_name: str | None = None


class UpdateRequest(BaseModel):
    offset: int | None = None
    limit: int | None = None
    timeout: int | None = None
    allowed_updates: list[str] | None = None


class Update(BaseModel):
    update_id: int
    message: Message | None = None
    callback_query: CallbackQuery | None = None
