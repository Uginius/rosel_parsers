import json
import os
import re
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Side, Border, PatternFill, Alignment
from openpyxl.styles.numbers import BUILTIN_FORMATS
from config import date_template, dir_template
from product_representation.src.prre_goals import oz_goals, wb_goals
from utilites import get_last_dir

shoplist = ['oz', 'wb']


def last_month_json_files(shop):
    folder = "product_representation/json_files"
    folder = os.path.join(folder, get_last_dir(folder))
    jsf = {}
    for filename in os.listdir(folder):
        find_date = re.findall(dir_template, filename)
        is_platform = shop in filename
        if find_date and is_platform:
            jsf[datetime.strptime(find_date[0], date_template)] = filename
    dates = jsf.keys()
    last = sorted(dates)[-1]
    last_month_files = {d: f'{folder}/{jsf[d]}' for d in dates if d.year == last.year and d.month == last.month}
    return last_month_files


class PrReMonthlyDataAnalytics:
    def __init__(self):
        self.json_filenames = {'oz': last_month_json_files('oz'), 'wb': last_month_json_files('wb')}
        self.goals_and_terms = {'oz': oz_goals, 'wb': wb_goals}
        self.current_goal = None
        self.platform_requests = {}
        self.platform_goods = []
        self.all_platform_goods = {}
        self.first_rq_in_category = {}
        self.categories = {}
        self.date = {}
        self.rosel_goods = {}
        self.workbook = Workbook()
        self.shop = None
        self.sheet = None
        self.req_id = None
        self.line_kpi = 0
        self.total_kpi = 0

    def run(self):
        self.initiate_workbook()
        self.platform_actions(shoplist[0])
        self.platform_actions(shoplist[1])
        last_date = list(self.all_platform_goods['oz'])[0]
        self.workbook.save(f"xls_result/{last_date.strftime('%Y-%B')}.xlsx")

    def platform_actions(self, platform):
        self.total_kpi = 0
        self.shop = platform
        self.get_json()
        self.add_caption()
        self.add_titles()
        self.add_body()
        self.set_total_kpi()

    def get_json(self):
        platform = self.shop
        goods = {}
        for date, filename in self.json_filenames[platform].items():
            print(f'opening {filename}')
            with open(filename, 'r', encoding='utf8') as file:
                self.rosel_goods = {}
                self.set_rosel_goods(file)
                goods.update({date: self.rosel_goods})
        self.rosel_goods = {}
        self.all_platform_goods[platform] = goods

    def set_rosel_goods(self, file):
        sellers = ['РОСЭЛ', 'Фотон', 'Safeline', 'Контакт', 'КОНТАКТ Дом', 'Рекорд', 'ORGANIDE']
        json_req = json.load(file)
        req, req_id = list(json_req.values())[0], list(json_req)[0]
        products = []
        for order, prod in req.items():
            prod_id = prod['shop_id']
            if prod['brand'] in sellers:
                if self.check_incorrect_goods(req_id, prod_id):
                    continue
                products.append({int(prod_id): [order, prod['name']]})
        self.rosel_goods[req_id] = products

    def check_incorrect_goods(self, req_id, prod_id):
        ban_prs = {'индикаторная отвертка': ['38710001', '79676933'], 'отвертка индикаторная': ['38710001', '79676933']}
        incorrect_product_id_detected = False
        if self.platform_requests[req_id] in ban_prs.keys():
            ban_list = ban_prs[self.platform_requests.get(req_id, None)]
            if prod_id in ban_list:
                incorrect_product_id_detected = True
        return incorrect_product_id_detected

    def add_caption(self):
        first_line = ['Отчет о представленности продукции по запросам на маркет-плейсах']
        platform = self.shop
        regions = {'oz': 'Москва', 'wb': 'Санкт-Петербург'}
        second_line = [f'Регион для которого осуществляется поисковая выдача - {regions[platform]}']
        self.sheet = self.workbook[platform]
        sw = self.sheet
        sw.append(first_line)
        sw.append([])
        sw.append(second_line)
        sw.append([])
        sw['A1'].font = Font(name='Calibri', size=20, color="000000", bold=True)
        sw.row_dimensions[1].height = 40
        sw.column_dimensions['A'].width = 35
        sw.column_dimensions['B'].width = 35
        sw.column_dimensions['C'].width = 7

    def add_titles(self):
        dates = [date.strftime('%d.%m.%Y') for date in self.all_platform_goods[self.shop]]
        products = ['Товары ' + date for date in dates]
        titles = ['Целевой запрос', 'Цель', 'КПД', *dates, *products]
        self.sheet.append(titles)
        self.add_titles_style(row_num=self.sheet.max_row, dates_quantity=len(dates))

    def add_titles_style(self, row_num, dates_quantity):
        sw = self.sheet
        thick = Side(border_style="thick", color="000000")
        first_date_column_number = ord('D')
        first_goods_column_number = first_date_column_number + dates_quantity
        for n in range(dates_quantity):
            date_column = chr(first_date_column_number + n)
            date_cell = sw[f'{date_column}{row_num}']
            date_cell.border = Border(top=thick, left=thick, right=thick, bottom=thick)
            date_column_dim = sw.column_dimensions[date_column]
            date_column_dim.width = 10
            date_column_dim.alignment = Alignment(horizontal='center')
            goods_column = chr(first_goods_column_number + n)
            goods_column_dim = sw.column_dimensions[goods_column]
            goods_column_dim.width = 50

    def add_body(self):
        platform = self.shop
        self.platform_goods = [date for date in self.all_platform_goods[platform].values()]
        goals = self.goals_and_terms[platform]
        self.req_id = None
        for self.req_id in self.platform_requests:
            self.check_category()
            self.current_goal = goals[self.req_id]
            self.set_body_lines()

    def set_body_lines(self):
        self.line_kpi = 0
        sw = self.sheet
        first_row_number = sw.max_row + 1
        req_id = self.req_id
        all_dates_shop_products_for_rq = [prods[req_id] for prods in self.platform_goods]
        products_q = [len(el) for el in all_dates_shop_products_for_rq]
        max_goods_q = max(products_q)
        prods = [prs for prs in all_dates_shop_products_for_rq]
        rq = self.platform_requests[req_id]
        if max_goods_q:
            self.body_lines_to_table(products_q=products_q, prods=prods, max_goods_q=max_goods_q)
        else:
            empty = [None] * len(products_q)
            kpi = None
            result = [rq, self.current_goal, kpi, *products_q, *empty]
            sw.append(result)
        self.merge_body_cells(fst_row=first_row_number, lens=products_q)
        # self.row_top_borders(current_row_number)

    def body_lines_to_table(self, products_q, prods, max_goods_q):
        dates_quantity = len(products_q)
        for el in prods:
            len_rq_prod_list = len(el)
            if len_rq_prod_list < max_goods_q:
                for num in range(len_rq_prod_list, max_goods_q):
                    el.append(None)
        prod_lines = [[prods[date][n] for date in range(dates_quantity)] for n in range(max_goods_q)]
        for n, prl in enumerate(prod_lines):
            second = []
            for pq in products_q:
                if pq == 0:
                    second.append(0 if n > pq - 1 else pq)
                else:
                    second.append(None if n > pq - 1 else pq)
            pr_names = []
            for p in prl:
                pr_names.append(p.order_name()) if p else pr_names.append(None)
            kpi = None
            result = [self.platform_requests[self.req_id], self.current_goal, kpi, *second, *pr_names]
            self.sheet.append(result)

    def merge_body_cells(self, fst_row, lens):
        max_q = max(lens)
        last_row = fst_row + max_q - 1 if max_q else fst_row
        # last_row = fst_row + max_q - 1
        self.merge_abc(fst=fst_row, last=last_row, lens=lens)
        self.merge_goods_cells(first_row=fst_row, lens=lens)

    def merge_abc(self, fst, last, lens):
        sw = self.sheet
        sw[f'A{fst}'].alignment = Alignment(horizontal='left', vertical='center')
        sw[f'B{fst}'].alignment = Alignment(horizontal='left', vertical='center')
        sw[f'C{fst}'].alignment = Alignment(horizontal='center', vertical='center')
        if last:
            sw.merge_cells(f'A{fst}:A{last}')
            sw.merge_cells(f'B{fst}:B{last}')
            sw.merge_cells(f'C{fst}:C{last}')

    def merge_goods_cells(self, first_row, lens):
        sw = self.sheet
        first_cell = ord('D')
        rows = max(lens)
        for n, goods_in_page in enumerate(lens):  # 4 0 5 0
            column = chr(first_cell + n)
            cell = f'{column}{first_row}'
            if goods_in_page:
                last_row = first_row + goods_in_page - 1
                sw.merge_cells(f'{cell}:{column}{last_row}')
            else:
                last_row = first_row + rows - 1 if rows else first_row
                # last_row = first_row + rows - 1
                sw.merge_cells(f'{cell}:{column}{last_row}')
                column2 = chr(first_cell + n + len(lens))
                cell2 = f'{column2}{first_row}'
                sw.merge_cells(f'{cell2}:{column2}{last_row}')
            sw[cell].alignment = Alignment(horizontal='center', vertical='center')
            self.check_goals(cell, self.platform_goods[n][self.req_id])
            self.row_top_borders(first_row)
        kpi_cell = sw[f'C{first_row}']
        kpi_cell.value = self.line_kpi

    def check_goals(self, cl, goods):
        cell = self.sheet[cl]
        cond = self.is_conditions_true(cell=cell, goods=goods)
        color_yes = 'C4D79B'
        color_no = 'E6B8B7'
        color = color_yes if cond else color_no
        cell.fill = PatternFill("solid", fgColor=color)
        self.total_kpi += 1
        if cond:
            self.line_kpi += 1

    def row_top_borders(self, row_number):
        thin = Side(border_style="thin", color="000000")
        for cell in self.sheet[row_number]:
            cell.border = Border(top=thin)

    def is_conditions_true(self, cell, goods):
        match self.current_goal:
            case 'на 1 странице, по популярности':
                return True if cell.value > 0 else False
            case 'не менее 5 SKU на 1 странице, по популярности':
                return True if cell.value >= 5 else False
            case 'не менее 4 SKU на 1 странице, по популярности':
                return True if cell.value >= 4 else False
            case 'не менее 2 SKU на 1 странице, по популярности':
                return True if cell.value >= 2 else False
            case 'не ниже 5 строки, по популярности':
                top5 = []
                for prod in goods:
                    if prod:
                        if prod.order < 6:
                            top5.append(prod.order)
                # top5 = [prod.order for prod in goods if prod.order < 6]
                return True if top5 else False

    def check_category(self):
        if self.req_id not in self.first_rq_in_category.keys():
            return
        category_name = self.first_rq_in_category[self.req_id]
        self.sheet.append([category_name])
        max_row = self.sheet.max_row
        max_column = chr(ord('A') + self.sheet.max_column - 1)
        self.sheet.merge_cells(f'A{max_row}:{max_column}{max_row}')
        self.set_style_to_categoy_cell(max_row)

    def initiate_workbook(self):
        for shop in shoplist:
            self.workbook.create_sheet(shop)
        if 'Sheet' in self.workbook.sheetnames:
            self.workbook.remove(self.workbook['Sheet'])

    def set_style_to_categoy_cell(self, row_order):
        cat_font = Font(name='Calibri', size=11, color="000000", bold=True)
        thin = Side(border_style="thin", color="000000")
        category_cell = self.sheet[f'A{row_order}']
        category_cell.border = Border(top=thin, left=thin, right=thin, bottom=thin)
        category_cell.fill = PatternFill("solid", fgColor="a6a6a6")
        category_cell.font = cat_font
        rd = self.sheet.row_dimensions[row_order]
        rd.height = 15

    def set_total_kpi(self):
        sw = self.sheet
        row = sw.max_row
        kpi_result = f'=SUM(C7:C{row})/{self.total_kpi}'
        sw.append([None, None, kpi_result])
        result_cell = sw[f'C{row + 1}']
        result_cell.number_format = BUILTIN_FORMATS[10]
        pass
