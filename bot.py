TOKEN = "1686681856:AAH-6oXXS2diCu_X-6jQDaqThdtDP78LEMI"
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler
import random
import time

start_keyboard = [['/dice', '/timer', '/help']]
dice_keyboard = [['/one_hexagon', '/two_hexagon'],
                 ['/twentysided', '/back']]
timer_keyboard = [['/30_sec', '/1_min', '/5_min'],
                  ['/back']]
close_keyboard = [['/close']]

start_markup = ReplyKeyboardMarkup(start_keyboard, one_time_keyboard=False)
dice_markup = ReplyKeyboardMarkup(dice_keyboard, one_time_keyboard=False)
timer_markup = ReplyKeyboardMarkup(timer_keyboard, one_time_keyboard=False)
close_markup = ReplyKeyboardMarkup(close_keyboard, one_time_keyboard=False)


def start(update, context):
    update.message.reply_text(
        "Я бот-помощник(не только) для настольных игр. Что вам нужно",
        reply_markup=start_markup
    )


def dice(update, context):
    update.message.reply_text(
        "Я могу кинуть кубик за вас",
        reply_markup=dice_markup
    )


def timer(update, context):
    update.message.reply_text(
        "Я могу завести таймер за вас",
        reply_markup=timer_markup
    )


def close(update, context):
    if 'job' in context.chat_data:
        context.chat_data['job'].schedule_removal()
        del context.chat_data['job']
    unset_timer(update, context)


def timer30(update, context):
    set_timer(update, context, 30)


def timer60(update, context):
    set_timer(update, context, 60)


def timer300(update, context):
    set_timer(update, context, 300)


def back(update, context):
    update.message.reply_text(
        "Что ещё вам нужно",
        reply_markup=start_markup
    )


def dice6(update, context):
    n = random.randint(1, 6)
    update.message.reply_text(f"{n}")


def dice2x6(update, context):
    n = random.randint(1, 6)
    p = random.randint(1, 6)
    update.message.reply_text(f"{n}, {p}")


def dice20(update, context):
    n = random.randint(1, 20)
    update.message.reply_text(f"{n}")


def help(update, context):
    update.message.reply_text("/help помощь по командам\n"
                              "/start вызывает стартовую меню\n"
                              "/time выдает тебе время\n"
                              "/date выдает тебе дату\n"
                              "/unset_timer убрать текущий таймер\n"
                              "/dice перемещает в меню с киданиями кубика\n"
                              "/one_hexagon выдает число которое выкинул один шестигранный кубик\n"
                              "/two_hexagon выдает число которое выкинули каждый из двух шестигранных кубиков\n"
                              "/twentysided выдает число которое выкинул один двадцатигранный кубик\n"
                              "/timer перемещает в меню таймера\n"
                              "/30_sec заводит таймер на 30 секунд\n"
                              "/1_min заводит таймер на 60 секунд(1 минута)\n"
                              "/5_min заводит таймер на 300 секунд(5 минут)\n"
                              "/close останавливает таймер\n"
                              " остальной текст тебе просто перешлют")


def echo(update, context):
    update.message.reply_text(f"Я получил сообщение {update.message.text}")


def get_time(update, context):
    update.message.reply_text(time.asctime().split()[3])


def get_date(update, context):
    time_list = time.asctime().split()
    date = ' '.join((time_list[2], time_list[1], time_list[4]))
    update.message.reply_text(date)


def remove_job_if_exists(name, context):
    """Удаляем задачу по имени.
    Возвращаем True если задача была успешно удалена."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def finish_timer(context):
    """Выводит сообщение"""
    job = context.job
    delay = context.bot_data['delay']
    context.bot.send_message(job.context, text=f"{delay} секунд истекли", reply_markup=timer_markup)


def set_timer(update, context, delay):
    """Добавляем задачу в очередь"""
    chat_id = update.message.chat_id
    job = context.job_queue.run_once(
        finish_timer,
        delay,
        context=chat_id,
        name=str(chat_id)
    )
    context.chat_data['job'] = job
    context.bot_data['delay'] = delay
    text = f'засек {delay} секунд'
    update.message.reply_text(text, reply_markup=close_markup)


def unset_timer(update, context):
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Хорошо, таймер остановлен' if job_removed else 'Нет активного таймера.'
    update.message.reply_text(text, reply_markup=timer_markup)


def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher
    text_handler = MessageHandler(Filters.text, echo)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("dice", dice))
    dp.add_handler(CommandHandler("one_hexagon", dice6))
    dp.add_handler(CommandHandler("two_hexagon", dice2x6))
    dp.add_handler(CommandHandler("twentysided", dice20))
    dp.add_handler(CommandHandler("timer", timer))
    dp.add_handler(CommandHandler("30_sec", timer30))
    dp.add_handler(CommandHandler("1_min", timer60))
    dp.add_handler(CommandHandler("5_min", timer300))
    dp.add_handler(CommandHandler("back", back))
    dp.add_handler(CommandHandler("close", close))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("time", get_time))
    dp.add_handler(CommandHandler("date", get_date))
    dp.add_handler(CommandHandler("unset_timer", unset_timer))
    dp.add_handler(text_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
