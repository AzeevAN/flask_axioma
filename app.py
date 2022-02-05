from flask import Flask, jsonify, request
import json
import os
from datetime import datetime
from environs import Env

env = Env()
env.read_env()

app = Flask(__name__)
NAME_FILES_YANDEX = 'stock_data_yandex.json'
AUTHORIZATIONS_TOKEN = env.list("AUTHORIZATIONS_TOKEN")
AUTH_CREATE_TOKEN = env.str("AUTH_CREATE_TOKEN")


@app.route('/yandex/cart', methods=['POST'])
def post_cart_items():
    """
    Ответ по остаткам товара на запрос от яндекс корзины
    :return:
    """
    # https://yandex.ru/dev/market/partner-marketplace-cd/doc/dg/reference/post-cart.html
    authorization = request.headers.get('Authorization')
    if authorization is None:
        return 'Authorization token not specified', 401
    if authorization in AUTHORIZATIONS_TOKEN:
        request_data = request.get_json()
        items_data_bd = load_file_json()
        if items_data_bd is None:
            return 'Ошибка в работе сервера', 500
        items = []
        for item in request_data.get('cart').get('items'):
            feedId = item.get('feedId')
            sku = item.get('offerId')
            count_need = item.get('count')
            item_dict = search(sku, items_data_bd)
            if item_dict is None or len(item_dict) == 0:
                count = 0
            else:
                count = count_need if item_dict[0]['count'] >= count_need else item_dict[0]['count']
            items.append(
                {
                    'feedId': feedId,
                    'offerId': sku,
                    'count': count,
                    'delivery': count > 0
                }
            )
        items_cart = {'items': items}

        return jsonify({'cart': items_cart}), 200
    else:
        return 'Access denied, invalid authorization token', 401


@app.route('/yandex/order/accept', methods=['POST'])
def post_order_accept():
    # https://yandex.ru/dev/market/partner-marketplace-cd/doc/dg/reference/post-order-accept.html
    authorization = request.headers.get('Authorization')
    if authorization is None:
        return 'Authorization token not specified', 401
    if authorization in AUTHORIZATIONS_TOKEN:
        request_data = request.get_json()
        print(request_data)
        with open(f'{os.getcwd()}/order_accept.json', 'w', encoding='utf8') as file:
            json.dump(request_data, file, indent=4, ensure_ascii=False)

        return 'Success', 200

        # items = request_data.get('skus')
        # warehouse_id = request_data.get('warehouseId')
        #
        # datetime_now = datetime.now().astimezone().replace(microsecond=0).isoformat()
        #
        # if items is None or warehouse_id is None:
        #     return 'Не корректные данные в теле запроса', 400
        #
        # items_data_bd = load_file_json()
        # if items_data_bd is None:
        #     return 'Ошибка в работе сервера', 500
        #
        # data_items = []
        # for item_ in items:
        #     item_dict = search(item_, items_data_bd)
        #     if item_dict is None or len(item_dict) == 0:
        #         continue
        #     data_items.append(
        #         {'sku': item_,
        #          'warehouseId': warehouse_id,
        #          'items': [
        #              {'type': 'FIT',
        #               'count': item_dict[0]['count'],
        #               'updatedAt': datetime_now
        #               }
        #          ]
        #          }
        #     )
        # all_data = {'skus': data_items}
        #


        # # ОТВЕТ
        # HTTP / 1.1
        # 200
        # OK
        # ...
        #
        # {
        #     "cart":
        #         {
        #             "items":
        #                 [
        #                     {
        #                         "feedId": 12345,
        #                         "offerId": "4609283881",
        #                         "count": 3,
        #                         "delivery": true
        #                     },
        #                     {
        #                         "feedId": 12346,
        #                         "offerId": "4607632101",
        #                         "count": 1,
        #                         "delivery": false
        #                     }
        #                 ]
        #         }
        # }
        return jsonify(request_data), 200
    else:
        return 'Access denied, invalid authorization token', 401


@app.route('/yandex/order/status', methods=['POST'])
def post_order_status():
    # https://yandex.ru/dev/market/partner-marketplace-cd/doc/dg/reference/post-order-status.html
    authorization = request.headers.get('Authorization')
    if authorization is None:
        return 'Authorization token not specified', 401
    if authorization in AUTHORIZATIONS_TOKEN:
        request_data = request.get_json()
        print(request_data)
        # items = request_data.get('skus')
        # warehouse_id = request_data.get('warehouseId')
        #
        # datetime_now = datetime.now().astimezone().replace(microsecond=0).isoformat()
        #
        # if items is None or warehouse_id is None:
        #     return 'Не корректные данные в теле запроса', 400
        #
        # items_data_bd = load_file_json()
        # if items_data_bd is None:
        #     return 'Ошибка в работе сервера', 500
        #
        # data_items = []
        # for item_ in items:
        #     item_dict = search(item_, items_data_bd)
        #     if item_dict is None or len(item_dict) == 0:
        #         continue
        #     data_items.append(
        #         {'sku': item_,
        #          'warehouseId': warehouse_id,
        #          'items': [
        #              {'type': 'FIT',
        #               'count': item_dict[0]['count'],
        #               'updatedAt': datetime_now
        #               }
        #          ]
        #          }
        #     )
        # all_data = {'skus': data_items}
        #


        # # ОТВЕТ
        # HTTP / 1.1
        # 200
        # OK
        # ...
        #
        # {
        #     "cart":
        #         {
        #             "items":
        #                 [
        #                     {
        #                         "feedId": 12345,
        #                         "offerId": "4609283881",
        #                         "count": 3,
        #                         "delivery": true
        #                     },
        #                     {
        #                         "feedId": 12346,
        #                         "offerId": "4607632101",
        #                         "count": 1,
        #                         "delivery": false
        #                     }
        #                 ]
        #         }
        # }
        return jsonify(request_data), 200
    else:
        return 'Access denied, invalid authorization token', 401


@app.route('/yandex/stocks/create', methods=['POST'])
def post_stocks():
    """
    Обновление данных остатков
    Загрузка остатков
    :return:
    """
    authorization = request.headers.get('Authorization')
    if authorization is None:
        return 'Authorization token not specified', 401
    if authorization != AUTH_CREATE_TOKEN:
        return 'Access denied, invalid authorization token', 401
    request_data = request.get_json()
    if request_data is None:
        return 'Error', 400
    with open(f'{os.getcwd()}/{NAME_FILES_YANDEX}', 'w', encoding='utf8') as file:
        json.dump(request_data, file, indent=4, ensure_ascii=False)

    return 'Data loaded successfully', 201


@app.route('/yandex/stocks', methods=['POST'])
def get_item_stock():
    """
    Метод возвращает данные по остаткам в базе для указанных артикулов
    :return:
    """
    authorization = request.headers.get('Authorization')
    if authorization is None:
        return 'Authorization token not specified', 401

    if authorization in AUTHORIZATIONS_TOKEN:
        request_data = request.get_json()
        items = request_data.get('skus')
        warehouse_id = request_data.get('warehouseId')

        datetime_now = datetime.now().astimezone().replace(microsecond=0).isoformat()

        if items is None or warehouse_id is None:
            return 'Не корректные данные в теле запроса', 400

        items_data_bd = load_file_json()
        if items_data_bd is None:
            return 'Ошибка в работе сервера', 500

        data_items = []
        for item_ in items:
            item_dict = search(item_, items_data_bd)
            if item_dict is None or len(item_dict) == 0:
                continue
            data_items.append(
                {'sku': item_,
                 'warehouseId': warehouse_id,
                 'items': [
                     {'type': 'FIT',
                      'count': item_dict[0]['count'],
                      'updatedAt': datetime_now
                      }
                 ]
                 }
            )
        all_data = {'skus': data_items}

        return jsonify(all_data), 200
    else:
        return 'Access denied, invalid authorization token', 401


def search(name, data_list):
    """
    Поиск нужного артикула в списке базы данных
    :param name:
    :param data_list:
    :return:
    """
    return [element for element in data_list if element['sku'] == name]


def load_file_json():
    """
    загрузка данных в словарь из базы
    :return:
    """
    new_value = None
    with open(f'{os.getcwd()}/{NAME_FILES_YANDEX}', 'r', encoding='utf-8') as file:
        new_value = json.load(file)

    return new_value


if __name__ == '__main__':
    app.run(port=8000, host='0.0.0.0')
