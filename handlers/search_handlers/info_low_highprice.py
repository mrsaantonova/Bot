import requests
from loader import bot
from telebot.types import Union, CallbackQuery, Message
from states.hotel_information import HotelInfoState, BestDealState
from utils.api_requests.hotels_request import post_hotels_request
from utils.api_requests.detail_request import post_detail_request
from random import choice
from keyboards.inline.all_keyboards import row_address_and_on_map
from loguru import logger
from database.hotels_db import HotelLowPrice, HotelHighPrice


@logger.catch
@bot.message_handler(state=HotelInfoState.info_low_high)
def info_low_high(message: Union[CallbackQuery, Message]) -> None:
    """
    Хэндлер состояния вывода информации по командам: /lowprice и /highprice.
    Устанавливает состояния минимальной цены для команды /bestdeal.
    Конечное состояние для команд: /lowprice и /highprice
    """
    if message.text == ('Да', 'да'):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            is_best_deal = data['is_best_deal']

        if is_best_deal:
            bot.set_state(message.from_user.id, BestDealState.price_min, message.chat.id)
            bot.send_message(message.from_user.id, choice(['Введите минимальную цену для поиска($)',
                                                           'Нужна минимальная цена для поиска ($)',
                                                           'Пожалуйста, введите минимальную цену для поиска ($)']))
        else:
            if data['need_photo']:
                full_info = f"Чудесно!\nВаш запрос:\n" \
                            f'"Самые {data["cost"]} отели в городе"\n' \
                            f"Город: {data['city']}\n" \
                            f"Количество отелей: {data['hotel_amt']}\n" \
                            f"Количество фотографий: {data['photo_amt']}"
            else:
                full_info = f"Отлично!\nВаш запрос:\n" \
                            f'"Самые {data["cost"]} отели в городе"\n' \
                            f"Город: {data['city']}\n" \
                            f"Количество отелей: {data['hotel_amt']}\n" \
                            f"Без фотографий"

            bot.send_message(message.from_user.id, full_info)
            bot.send_message(message.from_user.id, choice(['Ожидайте...',
                                                           'Можно 💤? Ждём...',
                                                           'Тик-так ⌛ Ожидаем...',
                                                           'Надеюсь моя 🔋 не сядет...\n'
                                                           'Шучу😉 Просто чуток подождем...',
                                                           'Возьмите пока что 🎧\n'
                                                           'И немного подождем...']))

            low_to_high = "PRICE_LOW_TO_HIGH"
            high_to_low = "PRICE_HIGH_TO_LOW"

            if data['is_low_price']:
                sorting = low_to_high
                owner = data['user_low']
            else:
                sorting = high_to_low
                owner = data['user_high']

            offers = post_hotels_request(data['cityID'], data['hotel_amt'], sorting)

            if sorting == "PRICE_LOW_TO_HIGH":
                sort_val = sorted(offers.items(), key=lambda val: int(val[1][1][1:]))
            else:
                sort_val = sorted(offers.items(), key=lambda val: int(val[1][1][1:]), reverse=True)
            if offers and not data['need_photo']:
                bot.send_message(message.from_user.id, choice(['Подобраны следующие варианты:',
                                                               'Что удалось подобрать:',
                                                               'Подобрал следующее:']))
                count = 1

                for i_info in sort_val:
                    bot.send_message(message.from_user.id,
                                     f'{count}. <b>{i_info[1][0]}</b>\n'
                                     f'<i>Цена: {i_info[1][1]}</i>',
                                     parse_mode='html')
                    if data['is_low_price']:
                        HotelLowPrice.create(owner=owner,
                                             city=data['city'],
                                             name=i_info[1][0],
                                             price=i_info[1][1])
                    else:
                        HotelHighPrice.create(owner=owner,
                                              city=data['city'],
                                              name=i_info[1][0],
                                              price=i_info[1][1])
                    count += 1
                else:
                    bot.delete_state(message.from_user.id, message.chat.id)

            elif offers and data['need_photo']:
                bot.send_message(message.from_user.id, choice(['Подобраны следующие варианты:',
                                                               'Что удалось подобрать:',
                                                               'Подобрал следующее:']))
                count = 1

                for i_offer in sort_val:
                    offer_with_photo = post_detail_request(i_offer[0], data['photo_amt'])

                    bot.send_message(message.from_user.id,
                                     f'{count}. <b>{i_offer[1][0]}</b>\n'
                                     f'<i>Цена: {i_offer[1][1]}</i>',
                                     parse_mode='html')
                    if data['is_low_price']:
                        HotelLowPrice.create(owner=owner,
                                             city=data['city'],
                                             name=i_offer[1][0],
                                             price=i_offer[1][1])
                    else:
                        HotelHighPrice.create(owner=owner,
                                              city=data['city'],
                                              name=i_offer[1][0],
                                              price=i_offer[1][1])
                    count += 1

                    for i_name, i_lst in offer_with_photo.items():
                        if i_name not in ('address', 'static_img'):
                            for i_dct in i_lst:
                                for i_url, i_desc in i_dct.items():
                                    photo_file = requests.get(i_url)
                                    bot.send_photo(message.from_user.id,
                                                   photo_file.url,
                                                   caption=f'{i_desc}')
                else:
                    bot.delete_state(message.from_user.id, message.chat.id)
            else:
                bot.send_message(message.from_user.id, choice(['Произошла какая-то ошибка на сервере.\n'
                                                               'Попробуйте выбрать другой город',
                                                               'Что-то пошло не так...\n'
                                                               'Попробуйте выбрать другой город',
                                                               'Что-то случилось на сервере\n'
                                                               'Выберите другой город']))

    else:
        bot.send_message(message.from_user.id, choice(['Скажите же мне "Да"',
                                                       'Ну прошу Вас 🙏\n'
                                                       'Введите "Да"',
                                                       'Так хочется поделиться информацией😩\n'
                                                       'Жду Ваше "Да"',
                                                       '"Да"🥱']))