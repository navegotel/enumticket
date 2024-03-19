"""This sample script shows how to generate different imposition layouts
just with a few lines of code. For more information look into the code.
"""

import ticket
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A3
from reportlab.pdfgen import canvas
from reportlab.lib.colors import red

def impose_simple_counter():
    # create ticket with width and height
    t = ticket.Ticket(68*mm, 97*mm)
    # add background image
    t.add_drawable(ticket.Image("samples/numbered_ticket_jazz_01.png"))
    # add counter and specify position from left (22mm) and bottom (5mm)
    t.add_drawable(ticket.Counter(22*mm, 5*mm, fontname='Courier-Bold', fontsize=14))
    # create a page layout and specify how you want to imposte the tickets
    # the counter depends on the page layout which is why counter properties
    # such as number of tickets and counter offset are specified here
    layout = ticket.PageLayout(t, 100, numoffset=100, pagesize=A3, bleed=2*mm, bottom=10*mm, left=6*mm, top=10*mm, right=6*mm)
    # create a reportlab canvas to draw on
    c = canvas.Canvas('samples/numbered_ticket_jazz_01.pdf', layout.pagesize)
    # run generate method. The order in this example is sequential. In
    # production you will most likely want this to be STACKORDER
    layout.generate(c, order=ticket.SEQUENTIALORDER, cropmarks=True)
    # don't forget to save the canvas, otherwise you will end up with an empty pdf file
    c.save()

def impose_names():
    t = ticket.Ticket(68*mm, 97*mm)
    t.add_drawable(ticket.Image("samples/numbered_ticket_jazz_02.png"))
    # this time we add a label. Each ticket will show a name from the
    # list that is passed to the PageLayout instance.
    t.add_drawable(ticket.Label(22*mm, 5*mm, fontname='Times-BoldItalic', fontsize=12))
    t.add_drawable(ticket.Counter(7*mm, 5*mm, fontname='Times-BoldItalic', fontsize=32, digits=2))
    #Create a list with names from a text file
    name_list = []
    with open("samples/names.txt", "r") as f:
        for line in f:
            name_list.append(line.rstrip())
    # pass the name list to the page layout. In this example the length
    # of the name list is used to specify the number of tickets.
    layout = ticket.PageLayout(t, len(name_list), pagesize=A3, bleed=2*mm, bottom=10*mm, left=6*mm, top=10*mm, right=6*mm, labels=name_list)
    c = canvas.Canvas('samples/numbered_ticket_jazz_02.pdf', layout.pagesize)
    layout.generate(c, order=ticket.SEQUENTIALORDER, cropmarks=True)
    c.save()
    
def impose_names_rotated():
    t = ticket.Ticket(68*mm, 97*mm)
    t.add_drawable(ticket.Image("samples/numbered_ticket_jazz_02.png"))
    t.add_drawable(ticket.Label(22*mm, 5*mm, fontname='Times-BoldItalic', fontsize=12))
    t.add_drawable(ticket.Counter(7*mm, 5*mm, fontname='Times-BoldItalic', fontsize=32, digits=2))
    t.add_drawable(ticket.VerticalLabel(60*mm, 20*mm, fontname='Courier-Bold', fontsize=10))
    name_list = []
    with open("samples/names.txt", "r") as f:
        for line in f:
            name_list.append(line.rstrip())
    layout = ticket.PageLayout(t, len(name_list), pagesize=A3, bleed=2*mm, bottom=10*mm, left=6*mm, top=10*mm, right=6*mm, labels=name_list)
    c = canvas.Canvas('samples/numbered_ticket_jazz_03.pdf', layout.pagesize)
    layout.generate(c, order=ticket.SEQUENTIALORDER, cropmarks=True)
    c.save()
    
    
def impose_numbers_rotated():
    t = ticket.Ticket(130*mm, 50*mm)
    t.add_drawable(ticket.Image("samples/numbered_ticket_horz_01.png"))
    t.add_drawable(ticket.Counter(120*mm, 8*mm, fontname='Courier-Bold', fontsize=16, alignment=ticket.ALIGNRIGHT))
    t.add_drawable(ticket.VerticalCounter(20*mm, 8*mm, fontname='Courier-Bold', fontsize=16))
    layout = ticket.PageLayout(t, 500, numoffset=1, pagesize=A3, bleed=2*mm, bottom=10*mm, left=10*mm, top=10*mm, right=10*mm)
    c = canvas.Canvas('samples/numbered_tickets_horz.pdf', layout.pagesize)
    layout.generate(c, order=ticket.STACKORDER, cropmarks=True)
    c.save()
    
    
if __name__ == "__main__":
    impose_simple_counter()
    impose_names()
    impose_names_rotated()
    impose_numbers_rotated()
