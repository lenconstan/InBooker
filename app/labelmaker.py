import io
import base64


import xhtml2pdf
import xhtml2pdf.pisa as pisa

def gen_pdf(html_source):
    """Returns a html file into a base64 encoded pdf file.
    gen_pdf(/path/data.html) or gen_pdf(render_template('label.html'))"""
    result = io.BytesIO()
    html = html_source
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    base64_pdf = base64.b64encode(result.getvalue()).decode()
    
    return base64_pdf

# def gen_pdf(html_source):
#     """Returns a html file into a base64 encoded pdf file.
#     gen_pdf(/path/data.html) or gen_pdf(render_template('label.html'))"""
#     result = io.BytesIO()
#     html = html_source
#
#     HTML(html).write_pdf(result)
#
#
#     base64_pdf = base64.b64encode(result.getvalue()).decode()
#     print(base64_pdf)
#     return base64_pdf
