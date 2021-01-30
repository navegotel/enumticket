import ticket
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A3
from reportlab.pdfgen import canvas
from reportlab.lib.colors import red

t = ticket.Ticket(84*mm, 62*mm)
t.add_drawable(ticket.Image("sample01.png"))
#t.add_drawable(ticket.Border(color=red))
t.add_drawable(ticket.Box(17*mm, 12*mm, 30*mm, 10*mm, bordercolor=red, borderwidth=1*mm))
t.add_drawable(ticket.Counter(20*mm, 15*mm, fontname='Courier-Bold', fontsize=20))

layout = ticket.PageLayout(t, 100, numoffset=100, pagesize=A3, bleed=2*mm)

c = canvas.Canvas('sample01.pdf', layout.pagesize)
#print(c.getAvailableFonts())
layout.generate(c, order=ticket.SEQUENTIALORDER, cropmarks=True)
c.save()
