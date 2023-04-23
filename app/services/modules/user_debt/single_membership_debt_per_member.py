from .... import models
from ...miscellaneous import union
from ..spending_cost_module.expense_group_distribution import sum_cost_payment


def adding_missing_members(dict_collection_payment: dict, dict_collection_cost: dict, group_members: list, dict_updating: str):
    list_of_payings = dict_collection_payment.keys()
    group_members_new = map(str, group_members)
    list_of_costings = dict_collection_cost.keys()
    union_list_pre = union(list_of_costings, list_of_payings)
    union_list = union(union_list_pre, group_members_new)
    if dict_updating == 'payment':
        for ind in range(len(union_list)):
            if union_list[ind] not in list_of_payings:
                dict_collection_payment.update({union_list[ind]: 0})
        return dict_collection_payment
    else:
        for ind in range(len(union_list)):
            if union_list[ind] not in list_of_costings:
                dict_collection_cost.update({union_list[ind]: 0})
        return dict_collection_cost


def difference_betwen_cost_and_payment(group_id: int, db) -> dict:
    group_payments_p = sum_cost_payment(group_id, 'payment', db)
    group_costs_p = sum_cost_payment(group_id, 'cost', db)
    group_members = db.query(models.ExpensesGroup.group_members).filter(
        models.ExpensesGroup.id == group_id).first()[0]
    group_payments = adding_missing_members(
        group_payments_p, group_costs_p, group_members, 'payment')
    group_costs = adding_missing_members(
        group_payments_p, group_costs_p, group_members, 'cost')
    difference_distribution = {}
    for pay_key, pay_val in group_payments.items():
        diff_val = pay_val - group_costs.get(pay_key)
        difference_distribution.update({pay_key: diff_val})
    return difference_distribution


def calculating_debt_distribution(group_id: int, user_id: int, db) -> dict:
    groups_list = difference_betwen_cost_and_payment(group_id, db)
    user_share_divider = sum(val for val in groups_list.values() if val > 0)
    if user_share_divider == 0:
        return {'debtors': {}, 'owing': {}}
    user_share = abs(groups_list.get(str(user_id))) / user_share_divider
    positives_ids = [key for key, val in groups_list.items() if val > 0]
    new_group_list = {key: val for key,
                      val in groups_list.items() if key != str(user_id)}
    debtors = {key: round(user_share * abs(val), 2) for key, val in new_group_list.items()
               if key not in positives_ids and groups_list.get(str(user_id)) > 0}
    owing = {key: round(user_share * abs(val), 2) for key, val in new_group_list.items()
             if key in positives_ids and groups_list.get(str(user_id)) < 0}
    return {'debtors': debtors, 'owing': owing}


def setting_per_group_debt_distribution(group_id: int, db):
    memberships_queried = db.query(models.ExpensesGroupMembers).filter(
        models.ExpensesGroupMembers.expenses_group_id == group_id).all()
    for membership in memberships_queried:
        memberships_queried_single = db.query(models.ExpensesGroupMembers).filter(
            models.ExpensesGroupMembers.expenses_group_id == group_id, models.ExpensesGroupMembers.user_id == membership.user_id)
        debt_distribution = calculating_debt_distribution(
            group_id, membership.user_id, db)
        memberships_queried_single.update(
            {'debt_distribution': debt_distribution})
        db.commit()
