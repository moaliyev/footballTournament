from django import template

register = template.Library()


@register.filter
def filterByCategory(data, category):
    return data.filter(group=category).order_by("-points")
