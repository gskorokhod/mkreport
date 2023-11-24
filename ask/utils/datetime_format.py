def explain_datetime_format(datetime_format):
    for code, explanation in FORMAT_EXPLANATIONS.items():
        datetime_format = datetime_format.replace(code, explanation)

    return datetime_format


FORMAT_EXPLANATIONS = {
        "%d": "<day>",
        "%m": "<month>",
        "%Y": "<year>",
        "%y": "<year (last two digits)>",
        "%H": "<hour (00-23)>",
        "%I": "<hour (01-12)>",
        "%p": "<AM/PM>",
        "%M": "<minute>",
        "%S": "<second>",
        "%f": "<microsecond>",
        "%z": "<UTC offset>",
        "%Z": "<timezone>",
        "%j": "<day of the year>",
        "%U": "<week number (Sunday as first day of week)>",
        "%W": "<week number (Monday as first day of week)>",
        "%c": "<locale’s appropriate date and time>",
        "%x": "<locale’s appropriate date>",
        "%X": "<locale’s appropriate time>",
        "%A": "<weekday (full name)>",
        "%a": "<weekday (abbreviated)>",
        "%B": "<month (full name)>",
        "%b": "<month (abbreviated)>",
        "%w": "<weekday (number, Sunday as 0)>"
    }