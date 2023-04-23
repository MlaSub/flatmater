from .... import models


def final_amount_real_expense(costs: list) -> dict:
    # this is used to sum up for each id total costs or payments
    new_list_of_costs = {}
    for cost in costs:
        for cost_ind, cost_val in cost.items():
            new_list_of_costs_keys = list(new_list_of_costs.keys())
            if cost_ind in new_list_of_costs_keys:
                new_amount = cost_val + new_list_of_costs.get(cost_ind)
                new_list_of_costs.update({cost_ind: new_amount})
            else:
                new_list_of_costs.update({cost_ind: cost_val})

    return new_list_of_costs


def sum_cost_payment(group_id: int, type: str, db) -> dict:
    # get all costs or payments
    type_of_sum = None
    if type == 'payment':
        type_of_sum = models.Expense.payment_division
    elif type == 'cost':
        type_of_sum = models.Expense.cost_division
    expense_array = db.query(type_of_sum).filter(
        models.Expense.expenses_group_id == group_id).all()
    list_of_expense_array = []
    for i in expense_array:
        list_of_expense_array.append(i[0])

    final_sum_dict = final_amount_real_expense(list_of_expense_array)
    return final_sum_dict


def real_expense_update(group_id: int, db) -> None:
    # updating ExpensesGroupMembers real_expense column for each member of the group
    payment_dict = sum_cost_payment(group_id, 'cost', db)
    for payment_ind, payment_val in payment_dict.items():
        expense_group_updating_query = db.query(models.ExpensesGroupMembers).filter(
            models.ExpensesGroupMembers.expenses_group_id == group_id, models.ExpensesGroupMembers.user_id == payment_ind)
        expense_group_updating_query.update({'real_expense': payment_val})
        db.commit()


def spent_update(group_id: int, db) -> None:
    # updating ExpensesGroupMembers sprent colomn for each member of the group
    spent_dict = sum_cost_payment(group_id, 'payment', db)
    print(spent_dict)
    for spent_ind, spent_val in spent_dict.items():
        expense_group_updating_query = db.query(models.ExpensesGroupMembers).filter(
            models.ExpensesGroupMembers.expenses_group_id == group_id, models.ExpensesGroupMembers.user_id == spent_ind)
        expense_group_updating_query.update({'spent': spent_val})
        db.commit()


def update_expense_group_members_spent_realexpense(group_id: int, db) -> None:
    spent_update(group_id, db)
    real_expense_update(group_id, db)
