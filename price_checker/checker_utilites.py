used_platforms = sorted([
    'baucenter', 'dns', 'maxidom', 'megastroy', 'petrovich', 'ststroitel', 'vprok'
])
shops_for_update_data = {
    'ach': 'auchan',
    'glo': 'globus',
    'lnt': 'lenta',
    'oke': 'okeydostavka',
}


def get_platform(shop_url):
    try:
        for shop in used_platforms:
            if shop in shop_url:
                return shop
    except TypeError:
        pass
    return None


def divide_goods_by_platforms(store):
    divided_goods = {}
    for order, url in store.items():
        shop = get_platform(url)
        if not shop in used_platforms:
            continue
        parser_id = f'{order:03}'
        if not divided_goods.get(shop):
            divided_goods[shop] = {}
        divided_goods[shop][parser_id] = url
    return divided_goods


if __name__ == '__main__':
    a = sorted(used_platforms)
    print(a)
