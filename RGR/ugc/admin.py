from django.contrib import admin
from .models import Profile
from .models import Message
from .forms import ProfileForm
from RGR.settings import TOKEN
import telebot

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'external_id', 'name')
    form = ProfileForm

@admin.register(Message)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'text', 'created_at', 'send')
    list_filter = ('send',)
    def show_message(self, request, queryset):
        bot_token = TOKEN
        bot = telebot.TeleBot(bot_token)
        message_text = "Бесплатные уроки и мастер-классы можете посмотреть здесь: https://www.livemaster.ru/ \nБесплатные уроки по шитью: https://www.livemaster.ru/masterclasses/shite \nБесплатные уроки по бисероплетению: https://www.livemaster.ru/masterclasses/rabota-s-biserom \nБесплатные уроки по макраме: https://www.livemaster.ru/masterclasses/kruzhevopletenie \nБесплатные уроки по вязанию: https://www.livemaster.ru/masterclasses/vyazanie \n"
        for message in queryset:
            chat_id = message.profile.external_id
            bot.send_message(chat_id, message_text)

        self.message_user(request, "Рассылка запущена")
    show_message.short_description = "Рассылка"

    actions = [show_message]

