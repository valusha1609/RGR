from django.core.management.base import BaseCommand
from django.conf import settings
import telebot
from telebot import TeleBot
from ugc.models import Profile
from ugc.models import Message



class DirectionBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.questions = [
            "",
            "1. Нравится ли Вам работать с тканью?",
            "2. Нравится ли Вам вязать?",
            "3. Хотели бы Вы поработать с бисером?",
            "4. Интересует ли Вас плетение?",
            "5. Привлекает ли Вас работа с пряжей?",
            "6. Нравится ли Вам шить?",
            "7. Интересует ли вас создание урашений?",
            "8. Привлекает ли Вас макраме?",
        ]
        self.current_question = 0

        self.directions = {
            'Бисероплетение': "Посетите мастер-классы по бисероплетению. Создавайте индивидуальные украшения, различные элементы декора, игрушки.",
            'Вязание' : "Советуем Вам сходить на мастер-классы по вязанию. Вы сможете с легкостью создавать различные предметы гардероба из пряжи своими руками.",
            'Шитье': "Шитье позволит Вам создать любой предмет гардероба своими руками. Изучив азы, проявляйте креативность и используйте другие техники.",
            'Макраме': "Техника макраме используется в декоре, для создания украшений и предметов интерьера вашей квартиры.",
        }

        self.user_responses = {}

    def restart(self, message):
        self.current_question = 0
        self.user_responses = {}
        self.start(message)

    def start(self, message):
        self.bot.send_message(message.chat.id, "Привет, я бот, который подскажет, каким хобби можно заняться, а также подберет мастер-классы под Ваше хобби. Начнем?")

    def ask_question(self, message):
        user_response = message.text.lower()
        if user_response == 'да' or user_response == 'нет':
            # Сохраняем ответ пользователя
            self.user_responses[self.current_question] = user_response

            self.current_question += 1

            if self.current_question < len(self.questions):
                self.bot.send_message(message.chat.id, self.questions[self.current_question])
            else:
                self.calculate_direction(message)
        else:
            self.bot.send_message(message.chat.id, "Пожалуйста, ответьте 'Да' или 'Нет'.")

    def calculate_direction(self, message):
    # Подсчет количества ответов "Да" для каждого направления
        directions_count = {direction: 0 for direction in self.directions}

        for question_num, answer in self.user_responses.items():
            if answer == 'да':
                for direction, question_numbers in settings.DIRECTIONS_QUESTIONS.items():
                    if question_num in question_numbers:
                        directions_count[direction] += 1

    # Выбор направления с максимальным количеством ответов "Да"
        max_count = max(directions_count.values())
        global recommended_direction
        recommended_directions = [direction for direction, count in directions_count.items() if count == max_count]

        if len(recommended_directions) == 1:
            recommended_direction = recommended_directions[0]
            response_text = self.directions.get(recommended_direction)
            self.bot.send_message(message.chat.id, response_text)
        else:
            self.bot.send_message(message.chat.id, "Мы не можем подобрать хобби для вас.")

        additional_question = "Хотели бы вы получать интересную информацию о мастер-классах?"
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.row('Да', 'Нет')
        self.bot.send_message(message.chat.id, additional_question, reply_markup=markup)   

    def handle_additional_question(self, message):
        user_response = message.text.lower()
        if user_response == 'да':
            self.bot.send_message(message.chat.id, "Отлично! Буду стараться радовать тебя информацией.")
            chat_id = message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=chat_id,
                defaults={'name': message.from_user.username}
            )
            Message(
                profile =p,
                text = recommended_direction,
                send = user_response,
            ).save()
            self.restart(message)
        elif user_response == 'нет':
            self.bot.send_message(message.chat.id, "Хорошо! Удачи в творческом пути.")
            chat_id = message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=chat_id,
                defaults={'name': message.from_user.username}
            )
            Message(
                profile =p,
                text = recommended_direction,
                send = user_response,
            ).save()
            self.restart(message)
        else:
            self.bot.send_message(message.chat.id, "Пожалуйста, ответьте 'Да' или 'Нет'.")

    def run(self):
        @self.bot.message_handler(commands=['start'])
        def handle_start(message):
            self.start(message)

        @self.bot.message_handler(func=lambda message: True)
        def handle_messages(message):
            if self.current_question < len(self.questions):
                self.ask_question(message)
            else:
                self.handle_additional_question(message)

        self.bot.polling()

class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **kwargs):
        bot = TeleBot(settings.TOKEN, threaded=False)
        direction_bot = DirectionBot(settings.TOKEN)
        direction_bot.run()