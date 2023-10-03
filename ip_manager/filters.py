from django.db.models import Q


def filter_ip_range(queryset, start_ip, end_ip):
    """
    Args:
        queryset (QuerySet): The queryset to filter.
        start_ip (str): The start IP address of the range.
        end_ip (str): The end IP address of the range.

    Returns:
        QuerySet: The filtered queryset.
    """

    return queryset.filter(Q(ip__ip__gte=start_ip) & Q(ip__ip__lte=end_ip))
