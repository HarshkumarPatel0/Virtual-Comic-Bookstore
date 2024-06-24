from datetime import datetime
from pony.orm import *
import os
import unicodedata
from encode import unpack, exists
import re


db = Database()
db.bind('sqlite', 'comics.sqlite', create_db=False)
#db.bind('sqlite', ':memory:', create_db=True)

LINK = re.compile(r"https?://\S+")

def normalize(text):
    nfkd_form = unicodedata.normalize('NFKD', text.lower())
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def comic_date(ymd):
    """
    11 bits for year
    5 bits for month
    5 bits for day
    For month
    0 Unknown
    Month * 2
    1 New Year
    3 Valentine's
    5 Spring Special
    7 Easter Special
    9 ?
    11 ?
    13 Summer Special
    15 ?
    17 ?
    19 Fall Special
    21 Halloween Special
    23 Winter Special
    25 Christmas Special
    27 Annual
    29 Other
    So we can sort numerically
    """
    try:
        year, month, day = map(int, ymd.split("-"))
        return day + month * 32 + year * 1024
    except:
        return 0

class Mixin(object):

    def search(self, field, value):
        pass

    @classmethod
    def fromGCD(cls, values, tables):
        pass

def getByName(cls, name, **kwargs):
    ascii = normalize(name)
    obj = cls.get(ascii=ascii)
    if obj is None:
        obj = cls(name=name, ascii=ascii, **kwargs)
        commit()
    return obj


class Era(db.Entity, Mixin):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    start_year = Required(int)
    end_year = Required(int)


class Scanner(db.Entity, Mixin):
    ascii = PrimaryKey(str)
    name = Required(str)
    group = Optional('Group')
    scans = Set('Scan')


class Scan(db.Entity, Mixin):
    id = PrimaryKey(int, auto=True)
    comic = Required('Comic')
    c2c = Required(bool)
    scanner = Optional(Scanner)
    pages = Set('Page')
    urls = Set('URL')
    files = Set('File')
    hash = Optional(str)
    size = Required(int)


class Group(db.Entity, Mixin):
    ascii = PrimaryKey(str)
    name = Required(str)
    scanners = Set(Scanner)


class Comic(db.Entity, Mixin):
    id = PrimaryKey(int, auto=True)
    scans = Set(Scan)
    date = Required(int)
    cover_date = Optional(str)
    publisher = Optional('IndiciaPublisher')
    issue = Optional(str)
    variant = Optional(str)
    volume = Optional(str)
    pages = Optional(int)
    notes = Optional(LongStr)
    isbn = Optional(str)
    barcode = Optional(str)
    title = Optional(str)
    brand = Optional('Brand')
    cover_price = Optional(str)
    series = Optional('Series')
    stories = Set('Story')
    reprints = Set('Reprint')
    ratings = Set('Rating')
    reading_list_entrys = Set('ReadingListEntry')
    historys = Set('History')

    @classmethod
    def fromGCD(cls, values, tables):
        date = comic_date(values[11])
        series = exists(tables, "gcd_series", values[5]) #Series.get(id=values[5])
        brand = exists(tables, "gcd_brand", values[8]) #Brand[values[8]]
        publisher = exists(tables, "gcd_indicia_publisher", values[12])
        if series:
            series = series.id
        if brand:
            brand = brand.ascii
        if publisher:
            publisher = publisher.ascii
        if values[14]:
            pages = int(values[14])
        else:
            pages = None

        comic = Comic(issue=values[1], volume=values[2], series=series, brand=brand,
                      cover_date=values[10], date=date, publisher=publisher, variant=values[27],
                      cover_price=values[13], pages=pages, notes=values[20],
                      isbn=values[24], barcode=values[28], title=values[30])
        commit()
        #print(values)
        #print(comic, comic.issue, comic.series, comic.brand, comic.cover_date, comic.cover_price,
        #      comic.pages, comic.notes)
        return comic

    @property
    def display_date(self):
        return IntDate(self, "date")

    @property
    def html_notes(self):
        notes = self.notes
        notes = notes.replace(r"\r\n\r\n", r"\r\n")
        notes = notes.replace(r"\r\n", "<br/>")
        urls = LINK.findall(notes)
        for url in urls:
            notes = notes.replace(url, f'<a href="{url}" target="_blank">{url}</a>')
        return notes

    @property
    def thumb(self):
        for scan in self.scans:
                thumb = os.path.join("static", "thumbs", f"{scan.id}.jpg")
                if os.path.exists(thumb):
                    return f'<a href="/view/{scan.id}"><img src="/static/thumbs/{scan.id}.jpg" class="w-100" /></a>'

        return '<img src="/static/images/missing.jpg" class="w-100" />'

    @property
    def series_name(self):
        if self.series:
            return self.series.name
        else:
            return "None"

class IntDate():

    def __init__(self, model, field):
        self.model = model
        self.field = field
        ymd = getattr(model, field)
        y = int(ymd // 1024)
        m = int(ymd // 64) & 15
        d = ymd & 31

        if ymd < 0:
            self.date = "New Scan"
        elif d:
            self.date = f"{y:04}/{m:02}/{d:02}"
        elif m:
            self.date = f"{y:04}/{m:02}"
        elif y:
            self.date = f"{y:04}"
        else:
            self.date = "?"

        """        
        11 bits for year
        5 bits for month
        5 bits for day
        For month
        0 Unknown
        Month * 2
        1 New Year
        3 Valentine's
        5 Spring Special
        7 Easter Special
        9 ?
        11 ?
        13 Summer Special
        15 ?
        17 ?
        19 Fall Special
        21 Halloween Special
        23 Winter Special
        25 Christmas Special
        27 Annual
        29 Other
        So we can sort numerically
        """

    def __str__(self):
        return self.date


class Brand(db.Entity, Mixin):
    ascii = PrimaryKey(str)
    name = Required(str)
    notes = Optional(LongStr)
    comics = Set(Comic)

    @classmethod
    def fromGCD(cls, values, tables):
        brand = getByName(Brand, values[1], notes=values[4])
        return brand

class Publisher(db.Entity, Mixin):
    ascii = PrimaryKey(str)
    name = Required(str, unique=True)
    start_year = Optional(int)
    end_year = Optional(int)
    notes = Optional(LongStr)
    series = Set('Series')
    indicias = Set("IndiciaPublisher")

    @classmethod
    def fromGCD(cls, values, tables):
        publisher = getByName(Publisher, values[1], start_year=values[3], end_year=values[4], notes=values[5])
        return publisher

class IndiciaPublisher(db.Entity, Mixin):
    ascii = PrimaryKey(str)
    name = Required(str, unique=True)
    parent = Optional(Publisher)
    start_year = Optional(int)
    end_year = Optional(int)
    notes = Optional(LongStr)
    comics = Set(Comic)

    @classmethod
    def fromGCD(cls, values, tables):
        publisher = exists(tables, "gcd_publisher", values[2])
        if publisher:
            publisher = publisher.ascii
        indiciaPublisher = getByName(IndiciaPublisher, values[1], parent=publisher,
                                     start_year=values[4], end_year=values[5], notes=values[7])
        return indiciaPublisher


class Series(db.Entity, Mixin):
    id = PrimaryKey(int, auto=True)
    comics = Set(Comic)
    name = Required(str)
    start_year = Optional(int)
    end_year = Optional(int)
    publisher = Optional(Publisher)
    notes = Optional(LongStr)

    @classmethod
    def fromGCD(cls, values, tables):
        publisher = exists(tables, "gcd_publisher", values[12])
        if publisher:
            publisher = publisher.ascii
        series = Series(name=values[1], start_year=values[4], end_year=values[6],
                        publisher=publisher, notes=values[16])
        commit()
        return series


class Page(db.Entity, Mixin):
    id = PrimaryKey(int, auto=True)
    index = Required(int)
    filename = Required(str)
    hash = Optional(str)
    width = Optional(int)
    height = Optional(int)
    page_type = Required('PageType')
    ocr = Optional(LongStr)
    scan = Required(Scan)


class PageType(db.Entity, Mixin):
    ascii = PrimaryKey(str)
    name = Required(str, unique=True)
    pages = Set(Page)


class Story(db.Entity, Mixin):
    id = PrimaryKey(int, auto=True)
    title = Optional(str)
    feature = Optional(str)
    sequence = Optional(int)
    page_count = Optional(int)
    writer = Optional('Creator')
    pencils = Optional('Creator')
    inks = Optional('Creator')
    genres = Set('Genre')
    characters = Set('Character')
    synopsis = Optional(LongStr)
    notes = Optional(LongStr)
    comic = Optional(Comic)
    next_part = Optional('Story', reverse='previous_part')
    previous_part = Optional('Story', reverse='next_part')
    see_also = Set('Story', reverse='see_also')

    @classmethod
    def fromGCD(cls, values, tables):
        page_count = values[5]
        if page_count is not None:
            page_count = int(page_count)
        writer = Creator.add(values[7])
        pencils = Creator.add(values[8])
        inks = Creator.add(values[9])

        comic = exists(tables, "gcd_issue", values[6])
        if comic:
            comic = comic.id

        story = Story(title=values[1], feature=values[3], sequence=values[4],
                      page_count=page_count, writer=writer, pencils=pencils, comic=comic,
                      inks=inks, synopsis=values[15], notes=values[17])
        commit()

        genres = values[13]
        characters = values[14]
        Genre.add(genres, story)
        Character.add(characters, story)
        #print(f"[{story.id}] {story.title} Writer:{story.writer} Pencils:{story.pencils} Inks:{story.inks}")
        #print(genres, characters)
        return story


class Creator(db.Entity, Mixin):
    ascii = PrimaryKey(str)
    name = Required(str)
    writers = Set(Story, reverse="writer")
    pencils = Set(Story, reverse="pencils")
    inks = Set(Story, reverse="inks")
    notes = Optional(LongStr)

    @classmethod
    def fromGCD(cls, values, tables):
        creator = getByName(Creator, values[1], notes=values[13]+values[14])
        return creator

    @classmethod
    def add(cls, names):
        for name in names.split(";"):
            ascii = normalize(name.strip())
            if ascii:
                creator = Creator.get(ascii=ascii)
                if creator:
                    return creator.ascii

class Genre(db.Entity, Mixin):
    ascii = PrimaryKey(str)
    name = Required(str)
    stories = Set(Story)

    @classmethod
    def add(cls, names, story):
        for name in names.split(";"):
            name = name.strip()
            if name:
                genre = getByName(Genre, name)
                genre.stories.add(story)


class Character(db.Entity, Mixin):
    ascii = PrimaryKey(str)
    name = Required(str)
    notes = Optional(LongStr)
    aka = Optional(str)
    stories = Set(Story)

    @classmethod
    def add(cls, names, story):
        for name in names.split(";"):
            name = name.strip()
            if "(" in name:
                name = name.split("(")[0].strip()
            if "[" in name:
                name = name.split("[")[0].strip()
            if name:
                character = getByName(Character, name)
                character.stories.add(story)

class Feature(db.Entity, Mixin):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    notes = Optional(LongStr)

    @classmethod
    def fromGCD(cls, values, tables):
        feature = Feature(name=values[2], notes=values[7])
        commit()
        return feature

class URL(db.Entity, Mixin):
    id = PrimaryKey(int, auto=True)
    url = Optional(str)
    scan = Optional(Scan)


class File(db.Entity, Mixin):
    id = PrimaryKey(int, auto=True)
    path = Optional(str, unique=True)
    scan = Required(Scan)


class Reprint(db.Entity, Mixin):
    id = PrimaryKey(int, auto=True)
    comics = Set(Comic)


class User(db.Entity, Mixin):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    ascii = Required(str)
    password = Required(str)  # Hash of password
    role = Optional(int, default=3)
    # 1 Super
    # 2 Admin
    # 3 Regular
    email = Required(str, unique=True)
    ratings = Set('Rating')
    historys = Set('History')


class Rating(db.Entity, Mixin):
    id = PrimaryKey(int, auto=True)
    rating = Required(int)
    user = Required(User)
    comic = Required(Comic)


class ReadingList(db.Entity, Mixin):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    ascii = Required(str)
    reading_list_entrys = Set('ReadingListEntry')
    historys = Set('History')


class ReadingListEntry(db.Entity, Mixin):
    id = PrimaryKey(int, auto=True)
    index = Required(float)
    reading_list = Required(ReadingList)
    comic = Required(Comic)


class History(db.Entity, Mixin):
    id = PrimaryKey(int, auto=True)
    comics = Optional(Comic)
    user = Required(User)
    date = Required(datetime)
    reading_list = Optional(ReadingList)
    index = Optional(float)  # Index for reading list


#db.generate_mapping(create_tables=True)
#db.generate_mapping()
