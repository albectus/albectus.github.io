#!/usr/bin/env python3
"""Сборка сайта ООО «Альбектус».

Все реквизиты и контакты — в site.config.json. Сборка: python3 build.py
Результат — папка dist/ (её и публикует хостинг). Зависимостей нет, только стандартная библиотека Python 3.

Локальный просмотр: python3 build.py --local && python3 -m http.server -d dist 8000
"""
import datetime
import html
import json
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
DIST = ROOT / "dist"

PENDING = '<span class="pending">уточняется</span>'

PAGES = {
    "index.html": {
        "path": "",
        "title": "ООО «Альбектус» — сопровождение коммерческих проектов и IT-решения для бизнеса",
        "description": "ООО «Альбектус» оказывает услуги по сопровождению бизнес-проектов, разработке IT-решений и организации взаимодействия с профильными исполнителями. Работаем с юридическими лицами и ИП по договору.",
        "robots": "index, follow",
        "sitemap": True,
    },
    "privacy.html": {
        "path": "privacy.html",
        "title": "Политика конфиденциальности — ООО «Альбектус»",
        "description": "Политика обработки персональных данных пользователей сайта ООО «Альбектус».",
        "robots": "index, follow",
        "sitemap": True,
    },
    "consent.html": {
        "path": "consent.html",
        "title": "Согласие на обработку персональных данных — ООО «Альбектус»",
        "description": "Текст согласия на обработку персональных данных при обращении через сайт ООО «Альбектус».",
        "robots": "index, follow",
        "sitemap": True,
    },
    "404.html": {
        "path": "404.html",
        "title": "Страница не найдена — ООО «Альбектус»",
        "description": "Страница не найдена.",
        "robots": "noindex",
        "sitemap": False,
    },
}


def esc(v):
    return html.escape(v or "", quote=True)


def val_html(v, link=None):
    if not v:
        return PENDING
    if link:
        return f'<a href="{esc(link)}">{esc(v)}</a>'
    return esc(v)


def main():
    local = "--local" in sys.argv
    cfg = json.loads((ROOT / "site.config.json").read_text(encoding="utf-8"))
    c = cfg["company"]

    if local:
        base_url = "http://localhost:8000/"
    elif cfg.get("custom_domain"):
        base_url = "https://" + cfg["custom_domain"].strip().strip("/") + "/"
    else:
        base_url = cfg["site_url"].rstrip("/") + "/"
    u = urlparse(base_url)
    rel = u.path if u.path.endswith("/") else u.path + "/"
    site_host = (u.netloc + u.path).rstrip("/")

    email = (c.get("email") or "").strip()
    phone = (c.get("phone") or "").strip()
    phone_link = "tel:" + re.sub(r"[^\d+]", "", phone) if phone else None

    jsonld = {"@context": "https://schema.org", "@type": "Organization",
              "name": c["name"], "legalName": c.get("full_name") or c["name"], "url": base_url}
    if email: jsonld["email"] = email
    if phone: jsonld["telephone"] = phone
    if c.get("inn"): jsonld["taxID"] = c["inn"]
    if c.get("address"): jsonld["address"] = c["address"]

    common = {
        "company_name": esc(c["name"]),
        "company_full_name": esc(c.get("full_name") or c["name"]),
        "inn_html": val_html(c.get("inn")),
        "ogrn_html": val_html(c.get("ogrn")),
        "address_html": val_html(c.get("address")),
        "email_html": val_html(email, "mailto:" + email if email else None),
        "phone_html": val_html(phone, phone_link),
        "email": esc(email),
        "form_disabled": "" if email else " disabled",
        "form_hint": ("После нажатия кнопки откроется ваша почтовая программа с подготовленным письмом. Данные не сохраняются на сайте."
                      if email else "Приём обращений через форму будет доступен в ближайшее время."),
        "hosting": esc(cfg.get("hosting", "")),
        "policy_date": esc(cfg.get("policy_date", "")),
        "site_host": esc(site_host),
        "base_url": esc(base_url),
        "rel": esc(rel),
        "year": str(datetime.date.today().year),
        "version": datetime.datetime.now().strftime("%Y%m%d%H%M"),
        "jsonld": json.dumps(jsonld, ensure_ascii=False).replace("</", "<\\/"),
    }

    partials = {p.stem: p.read_text(encoding="utf-8") for p in (SRC / "partials").glob("*.html")}

    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(SRC / "static", DIST)
    shutil.copytree(SRC / "assets", DIST / "assets")

    for name, meta in PAGES.items():
        tpl = (SRC / name).read_text(encoding="utf-8")
        tpl = re.sub(r"\{\{include:(\w+)\}\}", lambda m: partials[m.group(1)], tpl)
        data = dict(common, page_title=esc(meta["title"]), page_description=esc(meta["description"]),
                    page_path=meta["path"], robots=meta["robots"])
        out = re.sub(r"\{\{(\w+)\}\}", lambda m: data[m.group(1)], tpl)
        left = re.findall(r"\{\{[^}]*\}\}", out)
        if left:
            sys.exit(f"{name}: не подставлены {left}")
        (DIST / name).write_text(out, encoding="utf-8")

    today = datetime.date.today().isoformat()
    urls = "".join(f"  <url><loc>{base_url}{m['path']}</loc><lastmod>{today}</lastmod></url>\n"
                   for m in PAGES.values() if m["sitemap"])
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n", encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {base_url}sitemap.xml\n", encoding="utf-8")
    if cfg.get("custom_domain") and not local:
        (DIST / "CNAME").write_text(cfg["custom_domain"].strip() + "\n", encoding="utf-8")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")

    missing = [k for k in ("inn", "ogrn", "address", "email", "phone") if not c.get(k)]
    print(f"Собрано в {DIST} для {base_url}")
    if missing:
        print("Не заполнено в site.config.json:", ", ".join(missing))


if __name__ == "__main__":
    main()
