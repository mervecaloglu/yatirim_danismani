from django import template
from decimal import Decimal
import decimal

register = template.Library()

@register.filter
def mul(value, arg):
    """
    Çarpma işlemi için template filter
    Kullanım: {{ value|mul:arg }}
    """
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except (ValueError, TypeError, decimal.InvalidOperation):
        return 0

@register.filter
def div(value, arg):
    """
    Bölme işlemi için template filter
    Kullanım: {{ value|div:arg }}
    """
    try:
        if Decimal(str(arg)) == 0:
            return 0
        return Decimal(str(value)) / Decimal(str(arg))
    except (ValueError, TypeError, decimal.InvalidOperation):
        return 0

@register.filter
def sub(value, arg):
    """
    Çıkarma işlemi için template filter
    Kullanım: {{ value|sub:arg }}
    """
    try:
        return Decimal(str(value)) - Decimal(str(arg))
    except (ValueError, TypeError, decimal.InvalidOperation):
        return 0

@register.filter
def add_decimal(value, arg):
    """
    Toplama işlemi için template filter (decimal destekli)
    Kullanım: {{ value|add_decimal:arg }}
    """
    try:
        return Decimal(str(value)) + Decimal(str(arg))
    except (ValueError, TypeError, decimal.InvalidOperation):
        return 0
