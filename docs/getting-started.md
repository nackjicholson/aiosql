# Getting Started

## Philosophy

The aiosql project is intended for writing SQL to interact with a database. In contrast, most database libraries are intended to reduce the amount of SQL developers need to write. Why does aiosql take this alternative approach?

* Having alternatives is good. No application pattern, no matter how predominant, can fit all use cases.
* SQL is the most expressive and performant way to interact with a SQL database.
* When you are monitoring SQL queries running in your database, it's simpler to identify where a query came from if it is source controlled, named, and written by a human.
* Powerful tools like [DataGrip](https://www.jetbrains.com/datagrip/) and [psql](https://www.postgresql.org/docs/12/app-psql.html) can be used to develop and iterate on SQL code that you can save to a file and load into python with aiosql.

### About ORMs

ORMs and SQL Query Builders offer pythonic interfaces that generate and execute SQL on your behalf. They exist to ease development, but not to make it simpler. Inheriting object hierarchies, mixing data with behaviors, mirroring a database schema, and generating SQL are anything but simple. ORMs are usually introduced early in a project's life when requirements are limited and the payoff for moving fast is high. As a project grows, ORM objects and their relations grow too, they become a source of complexity and confusion.

aiosql doesn't solve any of these problems directly either, your application is still going to get more complex over time. You can write really bad SQL and you can write really bad python. But, with aiosql there is no mandate that all interaction with the database need go through a complicated network of related python objects that mirror your database schema. You gain the simplicity and flexibility of a system where the database and the application are intentionally separate and independent from each other. They can change independently. The architecture of your application and the boundaries you choose between it and your database is left to you.

The documentation for projects like [SQLAlchemy](https://www.sqlalchemy.org/) and [Django DB](https://docs.djangoproject.com/en/3.0/topics/db/) will give you the complete run down on why ORMs are a valuable and productive way to develop. I urge you to choose these projects over aiosql if you find that they fit the needs of your application better. If you're still here, great! Keep reading to learn how to write SQL you can load into python.

## Loading Queries

There are a few different ways to load queries into aiosql. You need to know the basics of how to define your queries so aiosql can find them, and how aiosql turns them into methods on a dynamic [`Queries`]() object. For more information reference the [Defining SQL Queries](./defining-sql-queries.md) docs.

### From a SQL File

Below is an example of a _blogs.sql_ file that defines a few queries to load.

```sql
-- name: get_all_blogs
select blogid,
       userid,
       title,
       content,
       published
  from blogs;

-- name: get_user_blogs
-- Get blogs with a fancy formatted published date and author field
    select b.blogid,
           b.title,
           strftime('%Y-%m-%d %H:%M', b.published) as published,
           u.username as author
      from blogs b
inner join users u on b.userid = u.userid
     where u.username = :username
  order by b.published desc;
```

The two things to notice in this file are the `--name: <name_of_method>` comments and the `:username` substitution variable. The comments that start with `--name:` are the magic of aiosql. They are used by [`aiosql.from_path`](./api.md#aiosqlfrom_path) to parse the file into separate methods by name. In the case of _blogs.sql_ we expect two methods that look like this.

```python
def get_all_blogs(self) -> List:
    pass

def get_user_blogs(self, username: str) -> List:
    pass
```

The `username` parameter of `get_user_blogs` will substitute in for the `:username` variable in the SQL.

### From Directories of SQL Files

### From a SQL String

## Calling Query Methods

Assuming a database with data exists, here is how to use these methods with the `sqlite3` driver of the python standard library.

```python
>>> import sqlite3
>>> import aiosql
>>> conn = sqlite3.connect("./mydb.sql")
>>> queries = aiosql.from_path("./blogs.sql", "sqlite3")
>>> queries.get_user_blogs(conn, username="bobsmith")
[(3, 'How to make a pie.', '2018-11-23 00:00', 'bobsmith'), (1, 'What I did Today', '2017-07-28 00:00', 'bobsmith')]
```

Visuraque terras! Est vocat causa, tribusque ille, ingens, cui et perque
nemorum? Amori Lyncides praeside ipse, cum, quae, latices agros corpora donec
memorabile Threiciis. Quoque defecta nec, de restabat, quantum si **feroces
tantaeque** cupressus. Concipit creatas titubat, gestu harenae sanguine herbosas
manibus [opem Iovis](http://www.ferut.net/) sermone, litora.

- Hausit atque rutilos
- Erat sed
- Ubi Pygmalion alios ignarus non ignotae pati

## Handling Results

Feriente advolat suo, [percussit Sparten Memnonis](http://mollia-dat.com/)
Icare, spectabilis. Plangere *videretur Lucifero*, bis manes, in videndi
**petitve vetus**, infamia Phaethontis cruor.

    if (readme - dotAutoresponder(fileVle, -1, tweakBarSwitch.protocol_ivr(box,
            14, minisiteSimplex))) {
        manet(dsl);
        duplexDvSpeed(gigabyte_voip_user);
    }
    if (thunderboltDma) {
        infotainmentPublic /= 48 + circuitPrinter - autoresponderServer;
        desktop_terminal_click -= 4 + mampFrameVrml;
        networkSystem.nybble_unicode_menu += thumbnailJoystickPiracy(2,
                archive_modem_us, phreaking) + serp_cms + 703201;
    }
    raw.rate_encoding_e.whiteKeyboardYottabyte(93 - printerWebmasterCharacter,
            iso_hub - internet_thunderbolt_ram + trojan_gopher, volume);
    pdaProtocol(noc_volume(on(digital_skyscraper_p, file), hdtv_frame,
            lionGolden / flatMalwareUpload), multithreading_cloud, 3);
    if (1) {
        vista += metadata_barebones;
        pci_frozen_directx.word_registry.netiquette_samba_white(
                title.recordBurnWord.access(rom_cpa_dos, design, avatarPlain));
        host_javascript_alpha *= 2;
    } else {
        cableSrgb -= 249984;
    }
