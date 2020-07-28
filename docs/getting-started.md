# Getting Started

## Philosophy

The aiosql project is for writing SQL to interact with a database. Most database libraries are intended to reduce the amount of SQL developers need to write. This project doesn't take that approach and here is why.

* Alternatives are good. No approach, no matter how predominant, can fit all use cases.
* SQL is the most expressive and performant way to interact with a SQL database.
* Identifying where a query came from is simpler when it is source controlled, named, and written by a human.
* Writing SQL in files gives you built-in compatibility with powerful SQL tools like [DataGrip](https://www.jetbrains.com/datagrip/) and [psql](https://www.postgresql.org/docs/12/app-psql.html).

### About ORMs

ORMs and SQL Query Builders offer object interfaces to generate and execute SQL. They exist to ease development, not to make it simpler. Inheriting object hierarchies, mixing data with behaviors, mirroring a database schema, and generating SQL are not simple. ORMs are introduced early in a project's life when requirements are limited and the need to move fast is paramount. As a project grows, ORM objects and their relations grow too, they become a source of complexity and coupling.

aiosql doesn't solve these problems directly either, your application will still get more complex with time. You can write bad SQL and bad python. But, with aiosql there is no mandate that all interaction with the database go through a complex network of related python objects that mirror a database schema. The only mandates are that you write SQL to talk to the database and python to use the data. From there you start with a system in which the database and the application are intentionally separate and independent from each other so they can change independently. The architecture of your application and the boundaries you choose between it and the database is left to you.

The documentation for projects like [SQLAlchemy](https://www.sqlalchemy.org/) and [Django DB](https://docs.djangoproject.com/en/3.0/topics/db/) can give you a better vision for the class of problems that ORMs do solve and the productivity gains they intend. Please choose these projects over aiosql if you find that they fit the needs of your application better.

## Loading Queries

This section goes over the three ways to make SQL queries available for execution in python. You'll learn the basics of defining queries so aiosql can find them and turn them into methods on a `Queries` object. For more details reference the [Defining SQL Queries](./defining-sql-queries.md) documentation.

### From a SQL File

Below is an example of a _blogs.sql_ file that defines two queries to load.

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

Notice the `--name: <name_of_method>` comments and the `:username` substitution variable. The comments that start with `--name:` are the magic of aiosql. They are used by [`aiosql.from_path`](./api.md#aiosqlfrom_path) to parse the file into separate methods accessible by the name. In the case of _blogs.sql_ we expect the following two methods to be available.

```python
def get_all_blogs(self) -> List:
    pass

def get_user_blogs(self, username: str) -> List:
    pass
```

The `username` parameter of `get_user_blogs` will substitute in for the `:username` variable in the SQL.

### From a Directory of SQL Files

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
