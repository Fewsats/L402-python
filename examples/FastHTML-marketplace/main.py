from fasthtml.common import *
import os
import uuid
from starlette.responses import RedirectResponse, FileResponse, PlainTextResponse
from starlette.datastructures import UploadFile
# from l402_decorator import FastHTML_l402_decorator
from l402.server import Authenticator, FastHTML_l402_decorator
from l402.server.invoice_provider import FewsatsInvoiceProvider
# from replit.object_storage import Client
from l402.server.macaroons import SqliteMacaroonService


# Set up Fewsats invoice provider
# 1. Sign up at app.fewsats.com
# 2. Create API Key
# 3a. Export env variable FEWSATS_API_KEY=fs_...
# or
# 3b. Pass the api key to the provider FewsatsInvoiceProvider(api_key="fs_...")
api_key = os.environ.get("FEWSATS_API_KEY")
fewsats_provider = FewsatsInvoiceProvider(api_key=api_key)

# Set up MacaroonService for storing authentication tokens. In this case,
# we'll use SQLite as the database. 
macaroon_service = SqliteMacaroonService()


# Initialize the L402 Authenticator
authenticator = Authenticator(location='localhost:8000',
                              invoice_provider=fewsats_provider,
                              macaroon_service=macaroon_service)


db = database('data/marketplace.db')
items = db.t.items
if items not in db.t:
    items.create(id=int, title=str, description=str, price=int, cover_image=str, file_path=str, pk='id')
Item = items.dataclass()

# Add Flexbox Grid CSS
flexboxgrid = Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/flexboxgrid/6.3.1/flexboxgrid.min.css", type="text/css")


app = FastHTML(hdrs=(picolink, flexboxgrid))
rt = app.route


@rt("/{fname:path}.{ext:static}")
async def get(fname: str, ext: str):
    return FileResponse(f'{fname}.{ext}')


@patch
def __ft__(self: Item):
    price = f'${self.price / 100:.2f}'
    cover_image = self.cover_image if self.cover_image else 'https://via.placeholder.com/250x200'
    return Div(
        Card(
            Img(src=cover_image, alt=self.title, cls="card-img-top"),
            Div(
                H3(self.title, cls="card-title"),
                P(self.description[:100] + '...' if len(self.description) > 100 else self.description, cls="card-text"),
                P(B("Price: "), price, cls="card-text"),
                A("Download", href=f"/download/{self.id}", cls="btn btn-primary"),
                cls="card-body"
            )
        ),
        id=f'item-{self.id}',
        cls="col-xs-12 col-sm-6 col-md-4 col-lg-3"
    )


def mk_form(**kw):
    input_fields = Fieldset(
        Label("Title", Input(id="new-title", name="title", placeholder="Heart of Gold", required=True, **kw)),
        Label("Description", Input(id="new-description", name="description", placeholder="3D Model of the spaceship Heart of Gold", required=True, **kw)),
        Label("Price", Input(id="new-price", name="price", placeholder="Price ($)", type="number", required=True, **kw)),
        Group(Label("Cover Image", Input(id="new-cover-image", name="cover_image", type="file", required=True, **kw)),
        Label("Item File", Input(id="new-file", name="file", type="file", required=True, **kw)))
    )
    return Form(
        Group(input_fields),
        Button("Upload"),
        hx_post="/",
        hx_target="#item-list",
        hx_swap="afterbegin",
        enctype="multipart/form-data"
    ) 

@rt("/")
async def get(request):
    upload_form = Card(H4("Upload a New Item Form"), mk_form(hx_target="#item-list", hx_swap="afterbegin"))
    gallery = Div(*reversed(items()), id='item-list', cls="row")
    return Titled("Marketplace", Main(upload_form, gallery, cls='container'))


@rt("/")
async def post(request):
    form = await request.form()
    print("Received form data:", form)
    for key, value in form.items():
        print(f"{key}: {type(value)} - {value}")
    
    item = Item(
        title=form.get('title'),
        description=form.get('description'),
        price=int(form.get('price')) if form.get('price') else None,
        cover_image='',
        file_path=''
    )
    
    cover_image = form.get('cover_image')
    if cover_image:
        content = await cover_image.read()
        filename = f"cover_{uuid.uuid4()}{os.path.splitext(cover_image.filename)[1]}"
        filepath = os.path.join('uploads', filename)
        os.makedirs('uploads', exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(content)
        item.cover_image = filepath
    
    file = form.get('file')
    if file:
        content = await file.read()
        filename = f"file_{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
        filepath = os.path.join('uploads', filename)
        os.makedirs('uploads', exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(content)
        item.file_path = filepath
    
    items.insert(item)
    
    return item.__ft__()

@rt("/download/{id:int}", methods=["GET"])
@FastHTML_l402_decorator(authenticator, lambda req: (100, 'USD', 'Download of an item'))
async def download_file(req, id: int):
    item = items.get(id)
    if not item or not item.file_path:
        return PlainTextResponse("File not found", status_code=404)
    
    file_path = item.file_path
    if not os.path.exists(file_path):
        return PlainTextResponse("File not found", status_code=404)
    
    return FileResponse(
        file_path,
        filename=os.path.basename(file_path),
        media_type='application/octet-stream'
    )

serve()