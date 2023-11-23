"""enumticket is a module to impose tickets on a sheet of paper
and enumerate them"""

from random import shuffle
from math import ceil
from collections import namedtuple
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import black, white

STACKORDER = 1
SEQUENTIALORDER = 2
RANDOMORDER = 4

ALIGNCENTER = 1
ALIGNLEFT = 2
ALIGNRIGHT = 4

Margins = namedtuple('Margins', ['bottom', 'left', 'top', 'right'])


class Drawable(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def draw(self, canvas, ticket):
        pass
      
        
class Border(Drawable):
    """
    Draw a border around the ticket. 
    For debugging mainly.
    """
    def __init__(self, color=black, linewidth=0.25*mm):
        super().__init__(0, 0)
        self.color = color
        self.linewidth = linewidth
        
    def draw(self, canvas, ticket):
        canvas.saveState()
        canvas.setStrokeColor(self.color)
        canvas.setLineWidth(self.linewidth)
        canvas.rect(ticket.x, ticket.y, ticket.width, ticket.height)        
        canvas.restoreState()
        
class Image(Drawable):
    """
    Draw a background image. The image should have
    the same proportions as the ticket, otherwise
    it will be distorsioned
    """
    def __init__(self, image):
        super().__init__(0, 0)
        self.image = image
        
    def draw(self, canvas, ticket):
        canvas.drawImage(self.image, ticket.x, ticket.y, 
                         width=ticket.width, height=ticket.height)
        
class Box(Drawable):
    """
    Draw a box with rounded corner. Can be used as background for 
    the counter
    """
    def __init__(self, x, y, width, height, bordercolor=black,
                 borderwidth=0.25*mm, background=white, radius=3*mm):
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.radius = radius
        self.bordercolor = bordercolor
        self.borderwidth = borderwidth
        self.background = background
        
    def draw(self, canvas, ticket):
        canvas.saveState()
        canvas.setStrokeColor(self.bordercolor)
        canvas.setFillColor(self.background)
        canvas.setLineWidth(self.borderwidth)
        canvas.roundRect(ticket.x+self.x, ticket.y+self.y, 
                         self.width, self.height, self.radius, 
                         stroke=1, fill=1)
        canvas.restoreState()
        

class Counter(Drawable):
    """
    Draw the counter as a number on the ticket
    """
    def __init__(self, x, y, color=None, fontname=None, fontsize=12, alignment=ALIGNLEFT):
        super().__init__(x, y)
        self.color = color
        self.fontname = fontname
        self.fontsize = fontsize
        self.alignment = alignment
        
    def draw(self, canvas, ticket, digits=5):
        fmt = "{0:0" + str(digits) + "d}"
        canvas.saveState()
        if self.color is not None:
            canvas.setFillColor(self.color)
        if self.fontname is not None:
            canvas.setFont(self.fontname, self.fontsize)
        if self.alignment == ALIGNLEFT:
            canvas.drawString(ticket.x+self.x, ticket.y+self.y, fmt.format(ticket.number))
        elif self.alignment == ALIGNRIGHT:
            canvas.drawRightString(ticket.x+self.x, ticket.y+self.y, str(ticket.number))
        elif self.alignment == ALIGNCENTER:
            canvas.drawCentredString(ticket.x+self.x, ticket.y+self.y, str(ticket.number))
        

class Ticket(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.background = None
        self.number = 0
        self.x = 0
        self.y = 0
        self.drawables = []
        
    def add_drawable(self, drawable):
        self.drawables.append(drawable)
        
    def set_origin(self, x, y):
        self.x = x
        self.y = y
        
    def set_number(self, number):
        self.number = number
        
    def paint(self, canvas):
        """
        Paint ticket on the canvas.
        If inc is true the ticket number is 
        increased after painting
        """
        for drawable in self.drawables:
            drawable.draw(canvas, self)


class PageLayout(object):
    """
    Layout of tickets for numbering and printing.
    
    Attributes
    ----------
    ticket: Ticket
        Representation of the ticket that is going to be numbered
        and laid out on the pages for print.
        
    numtickets: integer
        The number of tickets to be laid out.
        
    numoffst: integer
        The number from which to start counting for numbering
        the tickets.
        
    pagesize: tuple of floats
        Width and height of the page.
        
    cropmarks: tuple of floats
        Length and width of the cutting marks.
        
    bleed: float
        Amount of space the cropmarks are moved inwards for cutting
        
    bottom: float
        Bottom margin
    left: float
        Left margin
    top: float
        Top margin
    right: float
        Right margin
    """
    def __init__(self, ticket, numtickets, numoffset=0, pagesize=A4, cropmarks=(5*mm, 0.25*mm), bleed=2*mm, 
                 bottom=15*mm, left=15*mm, top=15*mm, right=15*mm):
        self.ticket = ticket
        self.numtickets = numtickets
        self.numoffset = numoffset
        self.cropmarks = cropmarks
        self.bleed = bleed
        self.colcount = None
        self.rowcount = None
        self.tickets_per_page = None
        self.tickets_on_last_page = None
        self.numpages = None
        self.minmargins = None
        self.pagesize = pagesize
        self.realmargins = None
        self.set_margins(Margins(bottom, left, top, right))
        self.usable_pagewidth = None
        self.usable_pageheight = None
        self.numbers=[]
        
    def set_margins(self, minmargins):
        """
        Setting the page margins will re-calculate the number of
        columns, the number of rows, the number of columns and the
        real margins, i.e. offsets from top, left, bottom and right
        Calculation depends on pagesize. If pagesize is None then 
        the method will return without throwing an exception.
        """
        if self.pagesize is None:
            return
        self.usable_pagewidth = self.pagesize[0] - 2 * self.cropmarks[0] - minmargins.left - minmargins.right
        self.usable_pageheight = self.pagesize[1] - 2* self.cropmarks[0] - minmargins.bottom - minmargins.top
        self.colcount = int(self.usable_pagewidth / self.ticket.width)
        self.rowcount = int(self.usable_pageheight / self.ticket.height)
        self.tickets_per_page = self.colcount * self.rowcount
        self.ticket_on_last_page = self.numtickets % self.tickets_per_page
        self.numpages = ceil(self.numtickets / self.tickets_per_page)
        self.minmargins = minmargins
        left = minmargins.left + self.cropmarks[0]
        right = left + self.colcount * self.ticket.width
        top = minmargins.top + self.cropmarks[0]
        bottom = top + self.rowcount * self.ticket.height
        self.realmargins = Margins(self.pagesize[1]-bottom, left, top, self.pagesize[0]-right)
        
        
    def set_pagesize(self, pagesize):
        """
        Real margins are re-calculated when setting the pagesize
        """
        self.pagesize = pagesize
        self.set_margins(self.minmargins)
        
    def paint_printable_area(self, canvas):
        """
        Paint a frame around the printable area.
        For debugging purposes.
        """
        canvas.saveState()
        canvas.setLineWidth(self.cropmarks[1])
        canvas.line(self.realmargins.left, self.realmargins.bottom,
                    self.realmargins.left, self.pagesize[1]-self.realmargins.top)
        canvas.line(self.realmargins.left, self.realmargins.bottom,
                    self.pagesize[0] - self.realmargins.right, self.realmargins.bottom)
        canvas.line(self.pagesize[0] - self.realmargins.right, self.realmargins.bottom,
                    self.pagesize[0] - self.realmargins.right, self.pagesize[1]-self.realmargins.top)
        canvas.line(self.realmargins.left, self.pagesize[1]-self.realmargins.top,
                    self.pagesize[0] - self.realmargins.right, self.pagesize[1]-self.realmargins.top)
                    
        canvas.restoreState()
        
    def paint_cropmarks(self, canvas):
        canvas.saveState()
        canvas.setLineWidth(self.cropmarks[1])
        canvas.setStrokeColor(black)
        for col in range(0, self.colcount):
            canvas.line(self.realmargins.left+col*self.ticket.width+self.bleed, self.realmargins.bottom,
                        self.realmargins.left+col*self.ticket.width+self.bleed, self.realmargins.bottom-self.cropmarks[0])
            canvas.line(self.realmargins.left+(col+1)*self.ticket.width-self.bleed, self.realmargins.bottom,
                        self.realmargins.left+(col+1)*self.ticket.width-self.bleed, self.realmargins.bottom-self.cropmarks[0])
                        
            canvas.line(self.realmargins.left+col*self.ticket.width+self.bleed, self.pagesize[1]-self.realmargins.top,
                        self.realmargins.left+col*self.ticket.width+self.bleed, self.pagesize[1]-self.realmargins.top+self.cropmarks[0])
            canvas.line(self.realmargins.left+(col+1)*self.ticket.width-self.bleed, self.pagesize[1]-self.realmargins.top,
                        self.realmargins.left+(col+1)*self.ticket.width-self.bleed, self.pagesize[1]-self.realmargins.top+self.cropmarks[0])
        for row in range(0, self.rowcount):
            canvas.line(self.realmargins.left, self.realmargins.bottom+self.bleed+row*self.ticket.height,
                        self.realmargins.left-self.cropmarks[0], self.realmargins.bottom+self.bleed+row*self.ticket.height)
            canvas.line(self.realmargins.left, self.realmargins.bottom+(row+1)*self.ticket.height-self.bleed,
                        self.realmargins.left-self.cropmarks[0], self.realmargins.bottom+(row+1)*self.ticket.height-self.bleed)
                        
            canvas.line(self.pagesize[0]-self.realmargins.right, self.realmargins.bottom+self.bleed+row*self.ticket.height,
                        self.pagesize[0]-self.realmargins.right+self.cropmarks[0], self.realmargins.bottom+self.bleed+row*self.ticket.height)
            canvas.line(self.pagesize[0]-self.realmargins.right, self.realmargins.bottom+(row+1)*self.ticket.height-self.bleed,
                        self.pagesize[0]-self.realmargins.right+self.cropmarks[0], self.realmargins.bottom+(row+1)*self.ticket.height-self.bleed)
            
        
        canvas.restoreState()
        
    def get_cell(self, col, row):
        """
        Compute origin of cell defined by column and row
        """
        x = self.realmargins.left + col * self.ticket.width
        y = self.pagesize[1] - self.realmargins.top - (row+1) * self.ticket.height
        return x, y
        
    def generate_numbers(self, order=STACKORDER, invert=False):
        for i in range(0, self.numpages):
                self.numbers.append([])
        currentpage = 0
        if order == SEQUENTIALORDER:
            for i in range(self.numoffset, self.numtickets+self.numoffset):
                if len(self.numbers[currentpage]) < self.tickets_per_page:
                    self.numbers[currentpage].append(i)
                else:
                    currentpage += 1
                    self.numbers[currentpage].append(i)
        elif order == RANDOMORDER:
            numbers = [i for i in range(self.numoffset, self.numtickets+self.numoffset)]
            shuffle(numbers)
            while len(numbers) > 0:
                if len(self.numbers[currentpage]) < self.tickets_per_page:
                    self.numbers[currentpage].append(numbers.pop())
                else:
                    currentpage += 1
                    self.numbers[currentpage].append(numbers.pop())
        elif order == STACKORDER:
            for i in range(self.numoffset, self.numtickets+self.numoffset):
                self.numbers[currentpage].append(i)
                if currentpage < self.numpages - 1:
                    currentpage += 1
                else:
                    currentpage = 0
        if invert is True:
            self.numbers.reverse()
                
        
    def generate(self, canvas, order=STACKORDER, cropmarks=True, invert=False):
        """
        Layout tickets on canvas.
        
        Parameters
        ----------
        
        canvas: Canvas
            Canvas instance the tickets are laid out on.
            
        order: int
            The order in which the tickets are numbered.
            SEQUENTIALORDER: Sequentially one after another on 
            every page, i.e. on each page from n to n+tickets-on-page.
            Best suited when pages are cut individually.
            RANDOMORDER: Tickets are numbered in random order.
            STACKORDER: When all pages are piled up, ordering is
            from top to bottom, i.e. ticket 1 is on top of ticket 2,
            etc. This way, when cutting the whole pile at once
            with a guillotine, the resulting stacks of tickets are
            already in the right order.
        
        invert: Boolean
            Invert the page order i.e. last page is first in document.
            Useful in case the printer output is piled up in reverse
            order.
        """
        self.generate_numbers(order=order, invert=invert)
        for numbers in self.numbers:
            col = 0
            row = 0
            if cropmarks is True:
                self.paint_cropmarks(canvas)
            for number in numbers:
                self.ticket.set_number(number)
                x,y = self.get_cell(col, row)
                self.ticket.set_origin(x, y)
                self.ticket.paint(canvas)
                if col < self.colcount - 1:
                    col += 1
                else:
                    col = 0
                    row +=1
            canvas.showPage()
                    
                    
        
        
        
