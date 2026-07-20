# Hephzibah Wears and Collections — E-commerce Website

A Django e-commerce site for **Hephzibah Wears and Collections** (leather
shoes, slippers, bags, men's luxury fabrics, Ankara, lace and jewelry — for
men and women), built around WhatsApp ordering instead of a card checkout.

Business details baked into the site:
- **Address:** AA3 Layout, Kuje, Abuja
- **Phone:** +234 708 287 1073
- **WhatsApp:** +234 906 883 2008

---

## 1. What's included

| Requirement | Where it lives |
|---|---|
| Admin dashboard (upload/edit/delete products, update prices, mark sold out, multiple images) | Django admin at `/admin/`, see `store/admin.py` |
| Product categories: Bags, Shoes, Accessories, Wholesale, New Arrivals | `store/models.py` (`Category`), seeded by `seed_data` |
| Search | `/search/?q=...`, see `store/views.py::search` |
| "Order on WhatsApp" button per product, business sees Name/Phone/Address/Items | `store/models.py::Order` + `OrderItem`, form on the product page, visible in `/admin/store/order/` |
| Wholesale enquiry page/form → business name, location, phone, monthly quantity | `/wholesale/`, `store/models.py::WholesaleEnquiry`, visible in `/admin/store/wholesaleenquiry/` |
| Royalty-free Unsplash photos | `store/management/commands/seed_data.py` (downloads real, free-to-use Unsplash photos into your product catalogue) |
| Your logo | `static/images/logo.png`, used in the header, footer and hero |
| Pagination, sorting & filtering | `store/views.py::_product_list_response`, see section 2 below |
| SEO (sitemap, robots.txt, Open Graph, structured data) | see section 3 below |

The visual design is a black-and-gold "crest & seal" theme built directly off
your logo — Cinzel for headings, Jost for body text, and a gold wax-seal motif
used for category markers, "New" badges and the "Sold Out" ink stamp.

---

## 2. Browsing: pagination, sorting & filtering

Category, "All Products" and search-result pages now show 12 products per
page (change `PRODUCTS_PER_PAGE` at the top of `store/views.py` to adjust),
with:
- **Sort by**: Newest, Price low→high, Price high→low, Name A–Z
- **Filter**: Men / Women / Men & Women, and an "in stock only" checkbox
- Prev/Next pagination that keeps whatever sort/filter/search is active

No setup needed — this works out of the box.

## 3. SEO

Also included, no setup needed:
- **`/sitemap.xml`** — auto-generated, lists every active product, category
  and the main pages. Submit this URL in Google Search Console once you're
  live.
- **`/robots.txt`** — allows crawling of the storefront, blocks `/admin/`,
  and points crawlers to the sitemap.
- **Open Graph / Twitter Card tags** on every page, and per-product ones
  (name, price, photo) on product pages — this is what makes a product
  look good when someone shares its link on WhatsApp, Instagram or Facebook.
- **Product structured data (JSON-LD)** on every product page, and
  business/store structured data on the home page — this is what lets
  Google show price/availability directly in search results.

## 4. Requirements

- Python 3.10+
- pip
- (Optional, for wholesale email notifications) an SMTP account, e.g. Gmail with an App Password

> **A note on how this was built:** this project was written and reviewed by
> hand in an offline sandbox that has no internet access, so it could not be
> installed or run here to take a live screenshot. The code follows standard,
> current Django 5 conventions throughout and every Python file has been
> syntax-checked — but please run through the steps below on your own machine
> and let me know if anything needs adjusting.

---

## 5. First-time setup

```bash
# 1. Unzip the project, then move into it
cd hephzibah

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your local settings
cp .env.example .env
# open .env and at minimum set a real SECRET_KEY — generate one with:
python -c "import secrets; print(secrets.token_urlsafe(50))"

# 5. Create the database tables
python manage.py makemigrations store
python manage.py migrate

# 6. Create your admin login
python manage.py createsuperuser

# 7. (Recommended) Populate categories + demo products with real Unsplash photos
#    — needs internet access to download the photos
python manage.py seed_data

# 8. Run the site
python manage.py runserver
```

Now visit:
- **Storefront:** http://127.0.0.1:8000/
- **Admin dashboard:** http://127.0.0.1:8000/admin/

Log into `/admin/` with the superuser you created in step 6. From there you
can add real products, upload real photos (drag in as many as you like per
product), change prices, and tick "Is sold out" whenever something runs out.

Delete the demo products from `/admin/store/product/` whenever you're ready
to replace them with your real catalogue (select them, choose "Delete" from
the action dropdown).

---

## 6. Using the admin dashboard

Go to **`/admin/`** and log in.

- **Store → Products**: add a product, choose its category, price, and
  gender. Scroll down to **Product images** to upload several photos at once
  — the first one becomes the main photo shown on product cards.
- Prices and the "sold out" tick-box can be edited directly from the product
  **list** page (no need to open each product).
- Use the **Action** dropdown on the product list to mark many products sold
  out / available in one click.
- **Store → Orders**: every "Order on WhatsApp" submission from the site
  appears here automatically, with the customer's name, phone, address and
  exactly what they ordered — even though payment itself happens on
  WhatsApp.
- **Store → Wholesale enquiries**: every "Become a Wholesale Partner"
  submission appears here, with business name, location, phone number and
  estimated monthly order quantity.
- **Store → Categories**: add, rename, or reorder the 5 categories.

---

## 7. How WhatsApp ordering works

1. A customer opens a product and fills in name, phone, delivery address and
   quantity.
2. Submitting the form saves an `Order` (and its `OrderItem`) to the
   database — so you always have a record, even if a WhatsApp chat is later
   deleted — then redirects the customer straight into a WhatsApp chat with
   your business number, with all their details and the product pre-filled
   in the message.
3. You reply on WhatsApp and share your payment details there, as requested.

The **wholesale enquiry** form works the same way: it saves to the database
first, then hands the boutique owner off to WhatsApp with their details
pre-filled.

To also receive wholesale enquiries by **email**, fill in the `EMAIL_HOST_USER`,
`EMAIL_HOST_PASSWORD` and `WHOLESALE_NOTIFY_EMAIL` values in your `.env` file
(see `.env.example`). If you leave them blank, enquiries are simply saved to
the database and shown to the customer via WhatsApp — nothing breaks.

---

## 8. About the product photos

`python manage.py seed_data` downloads a set of genuine, free-to-use photos
from Unsplash (leather shoes, bags, fabric, jewelry, slippers) directly into
your product catalogue, so the site doesn't look empty on day one. Unsplash's
license allows commercial use with no attribution required, but hot-linking
directly to someone else's example listings isn't the same as photographing
your own stock — swap these out for real photos of your own products in
`/admin/` as soon as you can. Run `python manage.py seed_data --flush` to
wipe the demo products first if you want to start clean.

---

## 9. Deploying to a real server

This project runs on SQLite and Django's dev server out of the box, which is
fine for trying things out but not for production. Before going live:

1. Set `DEBUG=False` in `.env`.
2. Set `ALLOWED_HOSTS` in `.env` to your real domain, e.g.
   `ALLOWED_HOSTS=hephzibahwears.com,www.hephzibahwears.com`.
3. Switch the database to Postgres or MySQL for anything beyond a small demo
   (SQLite doesn't handle concurrent writes well). Update the `DATABASES`
   block in `hephzibah/settings.py`.
4. Run `python manage.py collectstatic` — static files (CSS/JS/logo) will be
   collected into `staticfiles/` and served efficiently by WhiteNoise
   (already wired up in `settings.py` and `MIDDLEWARE`).
5. Run the app with a real WSGI server instead of `runserver`, e.g.:
   ```bash
   gunicorn hephzibah.wsgi:application --bind 0.0.0.0:8000
   ```
6. Put it behind Nginx/Caddy with HTTPS, and point your domain at it.
7. Uploaded product photos are stored under `media/` on disk by default —
   for a production host with an ephemeral filesystem (e.g. some free-tier
   hosts), switch to a cloud storage backend such as `django-storages` with
   S3/Cloudinary so uploads survive redeploys.

Any Django-friendly host works well here: Railway, Render, PythonAnywhere, a
plain VPS with Nginx + gunicorn, etc.

---

## 10. Project structure

```
hephzibah/
├── manage.py
├── requirements.txt
├── .env.example
├── hephzibah/            # project settings, URLs
├── store/                # the app: models, admin, views, forms
│   ├── models.py         # Category, Product, ProductImage, Order, OrderItem, WholesaleEnquiry
│   ├── admin.py          # the admin dashboard configuration
│   ├── views.py          # home, category, product detail + order form, search, wholesale
│   ├── forms.py          # OrderForm, WholesaleEnquiryForm
│   ├── management/commands/seed_data.py
│   └── templatetags/store_extras.py
├── templates/
│   ├── base.html
│   └── store/            # home, category, product_detail, wholesale, product card
├── static/
│   ├── css/style.css     # the black & gold "crest & seal" design system
│   ├── js/main.js
│   └── images/logo.png
└── media/                # uploaded product photos land here
```

---

## 11. Troubleshooting

- **`ModuleNotFoundError: No module named 'django'`** — you haven't activated
  your virtual environment, or haven't run `pip install -r requirements.txt`.
- **Images don't show after `seed_data`** — that command needs internet
  access to fetch photos from Unsplash; if it can't reach the internet it
  will still create the products, just without photos (add photos manually
  from `/admin/`).
- **`django.db.utils.OperationalError: no such table`** — run
  `python manage.py migrate`.
- **Static files (fonts/CSS) look unstyled after deploying** — run
  `python manage.py collectstatic` and make sure `DEBUG=False` and
  `ALLOWED_HOSTS` are set correctly.
