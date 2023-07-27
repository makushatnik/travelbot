from datetime import datetime
from utils.constants import DATETIME_FORMAT
from loader import bot, log
import handlers
from utils.set_bot_commands import set_default_commands


def main():
    """ Main function """
    set_default_commands(bot)
    log.info('Bot started at: %s' % datetime.now().strftime(DATETIME_FORMAT))
    bot.infinity_polling()
    # bot.add_custom_filter(custom_filters.StateFilter(bot))
    # bot.infinity_polling(skip_pending=True)
    # bot.polling(non_stop=True, interval=0)


if __name__ == '__main__':
    main()
