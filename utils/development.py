from html5print import HTMLBeautifier


def print_html5(html):
    print(HTMLBeautifier.beautify(html, 4))
