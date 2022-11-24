from operator import itemgetter


def order_applications(applications, order_by, order_rev):
    """
    Returns a list of ordered applications
    """
    if order_by and order_by in [
        "id",
        "status",
        "account_id",
        "assessment_deadline",
        "started_at",
        "last_edited",
    ]:
        applications = sorted(
            applications,
            key=itemgetter(order_by),
            reverse=int(order_rev),
        )
    return applications
