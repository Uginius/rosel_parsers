from openpyxl import load_workbook


def load_goals(ws, shop):
    res = {}
    for order, row in enumerate(ws, 1):
        rq_id = f'{shop}{order:03}'
        cat = row[0].value
        req = row[1].value
        goal = row[2].value
        res[rq_id] = {'category': cat, 'request': req, 'goal': goal}
    return res


prre_workbook = load_workbook('product_representation/src/repr_goals.xlsx')
oz_goals = load_goals(prre_workbook['OZ'], 'oz')
wb_goals = load_goals(prre_workbook['WB'], 'wb')
goals_and_terms = {'oz': oz_goals, 'wb': wb_goals}
