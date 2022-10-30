urls_lnt = [
    'https://lenta.com/search/?searchText=%D0%9A%D0%BE%D0%BD%D1%82%D0%B0%D0%BA%D1%82',
    'https://lenta.com/search/?searchText=%D0%A4%D0%BE%D1%82%D0%BE%D0%BD&page=1',
    'https://lenta.com/search/?searchText=%D0%A4%D0%BE%D1%82%D0%BE%D0%BD&page=2',
    'https://lenta.com/search/?searchText=%D0%A4%D0%BE%D1%82%D0%BE%D0%BD&page=3',
    'https://lenta.com/search/?searchText=Safeline',
    'https://lenta.com/search/?searchText=%D0%A0%D0%B5%D0%BA%D0%BE%D1%80%D0%B4',
]

end_link = '&apiKey=06U4652632&shuffle=true&strategy=vectors_extended,zero_queries&productsSize=20&regionId=1' \
           '&forIs=true&showUnavailable=false&withContent=false&withSku=false'
urls_ach = [f'https://autocomplete.diginetica.net/autocomplete?st=контакт{end_link}',
            f'https://autocomplete.diginetica.net/autocomplete?st=фотон{end_link}']

urls_glo = [
    'https://online.globus.ru/catalog/avto-dacha-remont/filter/brands-is-545670-or-245825-or-230840-or-280153/apply/'
]

srh = 'https://www.okeydostavka.ru/webapp/wcs/stores/servlet/SearchDisplay?categoryId=&storeId=10151&searchTerm='
urls_oke = [srh + 'фотон', srh + 'контакт', srh + 'рекорд', srh + 'safeline', ]
