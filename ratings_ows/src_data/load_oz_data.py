from openpyxl.reader.excel import load_workbook


def load_oz_xls_data(filename):
    workbook = load_workbook(filename)
    loaded_data = {}
    for order, row in enumerate(workbook.active, 1):
        if order < 2:
            continue
        loaded_data[f'{order:03}'] = {'shop_id': row[0].value, 'rosel_id': row[1].value, 'name': row[2].value,
                                      'trade_mark': row[3].value, 'url': row[5].value}
        # if order == 3:
        #     break
    return loaded_data


if __name__ == '__main__':
    data = load_oz_xls_data('rosel_goods_OZ.xlsx')
