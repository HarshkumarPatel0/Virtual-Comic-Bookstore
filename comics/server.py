#!/usr/bin/env python
import bottle
from bottle import route, post, run, template, static_file, abort, request, response, redirect
from pony.orm.integration.bottle_plugin import PonyPlugin
import webbrowser
import os
from decimal import Decimal
from tkinter import Tk, filedialog
from archive import Archive, IMAGES
from PIL import Image

from models import *

PAGE_SIZE = 50
THUMB_SIZE = (240, 320)

bottle.debug(True)
bottle.install(PonyPlugin())

# After the plugin is installed each request will be processed
# in a separate database session. Once the HTTP request processing
# is finished the plugin does the following:
#  * commit the changes to the database (or rollback if an exception happened)
#  * clear the transaction cache
#  * return the database connection to the connection pool

root = Tk() # pointing root to Tk() to use it as Tk() in program.
root.withdraw() # Hides small tkinter window.
root.attributes('-topmost', True) # Opened windows will be active. above all windows despite of selection.

SECRET = "ReadComics"  # Change on server to stop forgeries
MODELS = {}

def register(name, cls):
    MODELS[name] = cls

# Context that is always present for every request
default_context = {}


# Add the list of genres to the default context
def update_default():
    with db_session:
        default_context['genres'] = select(g for g in Genre if g.name != "Any")

class Error():

    _errors = [
        (re.compile(r"^Attribute \w+(?:\[\d+\])?\.(?P<field>\w+) is required$"), 'Please enter a value'),
        (re.compile(r"^(?P<error>[^:]+):(?P<field>\w+)$"), None),
        (re.compile(r"^.*UNIQUE constraint failed: \w+\.(?P<field>\w+)"), "Already an existing record"),
    ]

    def __init__(self):
        self._values = {}

    def reset(self):
        self._values = {}

    def __setattr__(self, key, value):
        if key.startswith("_"):
            # Private variables not part of the session
            return super().__setattr__(key, value)
        self._values[key] = value

    def __getattr__(self, item):
        """
        Provide access to error using . instead of having to use ["name"]
        :param item: The field to access
        :return: The value
        """
        return self(item)

    def __call__(self, item):

        if item.startswith("_"):
            # Private variables not part of the session
            return self.__getattribute__(item)
        text = self._values.get(item)
        if text:
            return '<div class="error">%s</div>' % text
        else:
            return ""

    def process(self, e: Exception):
        errmsg = str(e)
        print("Exception:", type(e), errmsg)
        for error, message in self._errors:
            print("Error:", type(error), error)
            match = error.match(errmsg)
            if match:
                groups = match.groupdict()
                print("Match found", groups)
                if not message:
                    message = groups["error"]
                if "field" in groups:
                    setattr(self, groups["field"], message)


# Serve the static resources
@route('/static/<filepath:path>')
def serve_static(filepath):
    return static_file(filepath, root='./static')


# Session variable that is sent to server as a cookie, to provide state
class Session():
    def __init__(self):
        self._values = {
            'user': None,
            'genre': 'Any',
        }

    @classmethod
    def get(cls):
        """
        Retrieve the session from cookie
        :return: The session variable
        """
        session = request.get_cookie("session", secret=SECRET)
        if session:
            return session
        # If no existing session create one
        session = cls()
        session._values['genre'] = 'Any'  # And set brand to the first instance (Any)
        return session

    def __getattr__(self, item):
        """
        Provide access to session using . instead of having to use ["name"]
        :param item: The field to access
        :return: The value
        """
        if item.startswith("_"):
            # Private variables not part of the session
            return self.__getattribute__(item)
        return self._values.get(item)

    def __setattr__(self, key, value):
        """
        Provide access to session using . instead of having to use ["name"]
        :param key: field
        :param value: value
        :return: None
        """
        if key.startswith("_"):
            # Private variable access should use default
            super().__setattr__(key, value)
        else:
            # If value changed then update the cookie
            if value != self._values.get(key):
                self._values[key] = value
                response.set_cookie("session", self, path="/", secret=SECRET)


# Fields to ignore on forms
ignore_fields = {
    'id', 'action', 'update', 'delete'
}

# A date matches this format
DATE = re.compile(r"^(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})$")
# A non integer value
DECIMAL = re.compile(r"^\d*\.\d+$")


class Page():
    """
    Base class to extend pages, automatically allows for authorized / unauthorized route
    """
    model = None  # The model that is used for CRUD

    def __init__(self, *args, **kwargs):
        """
        Create new page object
        :param args:
        :param kwargs:
        """
        self.out = False  # Have we output anything yet
        #  (since __next__ ia used this is how I keep track of whether we have output already)
        self.args = args
        self.kwargs = kwargs
        self.user = None

    def __iter__(self):
        return self

    def __next__(self):
        """
        Return the contents of the page request
        :return: The response
        """
        if self.out:
            raise StopIteration # Already returned
        self.out = True
        # We will be accessing the database
        with db_session:
            # Get the session variable
            self.session = Session.get()

            # Create a context for rendering the page
            context = default_context.copy()
            context.update(self.kwargs)
            context.update(self.session._values)
            # Path is the url that accessed this resource
            context['path'] = request.path
            # For providing generic form support
            form_title = ''
            form_submit = ''
            action = ''
            required = 'required'   # Use {{required}} in form so that they can be disabled in search mode
            if request.path.endswith("/add"):
                form_title = "Add New"
                form_submit = "Create"
                action = 'add'
            elif request.path.endswith("/search"):
                form_title = "Search For"
                form_submit = "Search"
                action = 'search'
                required = ''
            elif 'id' in self.kwargs:
                form_title = 'Edit'
                form_submit = 'Update'
                action = 'update'
            context['error'] = Error()
            context['form_title'] = form_title
            context['form_submit'] = form_submit
            context['action'] = action
            # The page name
            context['page_name'] = self.__class__.__name__
            context['required'] = required
            # Provide access to the session
            context['session'] = self.session
            context['genres'] = select(g.name for g in Genre)
            genre = self.session.genre
            # The current date
            context['today'] = datetime.now().strftime('%Y-%m-%d')
            instance = ''  # So we can display instance and get blank instead of None
            selection = []
            form_data = {}

            form = request.forms
            # Provide easy access to the form variables
            for key in form:
                value = form[key].strip()
                # coerce values
                if value:
                    args = value.split(':', 2)
                    if args[0] in MODELS and len(args) == 2:
                        if args[1].isdigit():
                            # Coerce ModelName:InstanceId into instance of ModelName
                            value = MODELS[args[0]][int(args[1])]
                        elif args[1] == "None":
                            value = None
                    elif key in {'model', 'username', 'password'}:
                        pass  # Could be numbers here, and we want to keep as strings
                    elif key == 'genre':
                        # Genre is numeric, so coerce into actual instance
                        value = Genre[value]
                    elif value.isdigit():
                        value = int(value)
                    elif DECIMAL.match(value):
                        value = Decimal(value)
                    elif DATE.match(value):
                        value = datetime.strptime(value, "%Y-%m-%d")
                context[key] = value
                if key not in ignore_fields and value:
                    # Update form data with value fields
                    form_data[key] = value

            if 'delete' in context:
                context['action'] = 'delete'

            # if we have a model
            if self.model:
                # and an id, then fetch the instance
                if 'id' in context:
                    instance = self.model[context['id']]
                    context['page'] = 1
                    context['pages'] = 1
                else:
                    # if no id, then select all the instances of the model
                    selection = select(i for i in self.model)
                    # if we are filtering then filter the selection 1 field at a time
                    if context['action'] == 'search' and request.method == "POST":
                        for field in form_data:
                            selection = self.model.filter(selection, field, form_data[field])


            page = int(request.query.page or '1')
            context['page'] = page
            context['selection'] = selection
            context['instance'] = instance

            # The active allows for active("class") to return active if "class" matches the class we are using
            context['active'] = lambda x: "active" if x == self.__class__.__name__ else ""

            # if request was a post
            if request.method == "POST":
                action = context['action']
                if action not in {'search', 'delete'}:
                    # for update or add we want to delegate the call
                    context['form_data'] = form_data
                    return self.__post__(**context)
                elif instance:
                    # We are deleting (search does not have instance)
                    instance.delete()
                    context['instance'] = ''
                    # select all of the model instances so we can list the updated one
                    context['selection'] = select(i for i in self.model)

            return self.__get__(**context)

    def __get__(self, **kwargs):
        abort(405, "Method not allowed.")

    def __post__(self, **kwargs):
        abort(405, "Method not allowed.")

    def render(self, page_template, kwargs):
        selection = kwargs['selection']
        count = selection.count()
        if count > PAGE_SIZE:
            page = kwargs['page']
            kwargs['objects'] = selection.page(page, PAGE_SIZE)
            kwargs['pages'] = int(count // PAGE_SIZE)
        else:
            kwargs['page'] = 1
            kwargs['pages'] = 1
            kwargs['objects'] = selection
        return template(page_template, **kwargs)

def extract_next(context):
    context['extract'] = select(comic for comic in Comic if comic.date == -1).first()
    return context['extract']


# Decorator so that we can handle crud pattern with single call
def dispatch(path):
    def decorator(f):
        route(path, method="GET", callback=f)
        route(path, method="POST", callback=f)
        route("%s/<id:int>" % path, method="GET", callback=f)
        route("%s/add" % path, method="GET", callback=f)
        route("%s/search" % path, method="GET", callback=f)
        return f

    return decorator

@route('/') # Main entry point
@route('/index.html') # Browsers check this
@dispatch('/comic')
class Comics(Page):
    model = Comic

    def __get__(self, **kwargs):
        instance = kwargs['instance']  # Adding as parameter removes from kwargs
        extract_next(kwargs)
        return self.render('comics', kwargs)

    def __post__(self, instance, form_data, **kwargs):
        # if instance, update existing else create new instance
        if instance:
            instance.set(**form_data)
        else:
            comic = Comic(**form_data)
        commit()
        return redirect("/comic")

@route('/extract/<id:int>')
class ExtractThumb(Page):
    def __get__(self, id=0, **kwargs):
        comic = Comic[id]
        comic.date = -2
        #print(comic)
        for scan in comic.scans:
            for file in scan.files:
                thumb = os.path.join("static", "thumbs", f"{scan.id}.jpg")
                if not os.path.exists(thumb):
                    archive = Archive(file.path)
                    #print("Type:", archive.isCb())
                    #print("Files:", [file for file in archive])
                    for filename, f in archive.contents():
                        print(filename, filename.extension)
                        if filename.extension in IMAGES:
                            with Image.open(f) as img:
                                print(filename, img.size)
                                img.thumbnail(THUMB_SIZE, Image.LANCZOS)
                                img.save(thumb)
                                return {}

        return {}


@route('/addscans')
class AddScans(Page):
    def __get__(self, **kwargs):
        if not extract_next(kwargs):

            # https://www.codegrepper.com/code-examples/python/How+to+open+dialog+box+to+select+folder+in+python
            comic_dir = filedialog.askdirectory()  # Returns opened path as str
            if not comic_dir:
                return redirect("/")
            comics = set(["cbr", "cbz", "zip", "rar"])
            with db_session:
                for subdir, dirs, files in os.walk(comic_dir):
                    for filename in files:
                        extension = filename.lower().split(".")[-1]
                        if extension in comics:
                            path = os.path.join(subdir, filename)
                            if not File.exists(path=path):
                                comic = Comic(date=-1, notes=path)
                                commit()
                                c2c = "c2c" in path.lower()
                                scan = Scan(comic=comic, size=os.path.getsize(path), c2c=c2c)
                                commit()
                                file = File(path=path, scan=scan)
                                commit()
                kwargs["selection"] = select(comic for comic in Comic if comic.date < 0)
                kwargs["form_title"] = None
            #extract_next(kwargs)
        else:
            kwargs["selection"] = select(comic for comic in Comic if comic.date < 0)
        return self.render('comics', kwargs)
        #return template('comics', **kwargs)

@route('/view/<id:int>')
class View(Page):
    def __get__(self, id=0, **kwargs):
        scan = Scan[id]
        for file in scan.files:
            archive = Archive(file.path)
            comic_dir = os.path.join("static", "comics", f"{id}")
            if not os.path.exists(comic_dir):
                os.mkdir(comic_dir)
            # print("Type:", archive.isCb())
            # print("Files:", [file for file in archive])
            files = []
            kwargs["files"] = files
            for i, (filename, f) in enumerate(archive.contents(), start=1):
                print(filename, filename.extension)
                if filename.extension in IMAGES:
                    files.append(f"/static/comics/{id}/{i}.{filename.extension}")
                    #out = os.path.join(comic_dir, filename.filename)
                    out = os.path.join(comic_dir, f"{i}.{filename.extension}")
                    if not os.path.exists(out):
                        with open(out, "wb") as output:
                            output.write(f.read())
        kwargs["thumb"] = f"/static/thumbs/{id}.jpg"
        return template('view', kwargs)


if __name__ == "__main__":
    # Generate object-database mapping
    db.generate_mapping(check_tables=False)
    db.create_tables()
    register('Comic', Comic)

    if False:
        webbrowser.open("http://www.localhost.com:8080/", new=2)
    run(host='www.localhost.com', port=8080, reloader=True)
