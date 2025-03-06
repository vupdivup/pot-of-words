# Pot of Words

Pot of Words is a RESTful dictionary API written in Python. Its underlying data is scraped from [Webster's Unabridged Dictionary](https://www.gutenberg.org/ebooks/29765), available under [Project Gutenberg](https://www.gutenberg.org/).

The following stack is used within the project:

| Technology | Usage
| - | - |
| [pandas](https://pandas.pydata.org/) | ETL
| [sqlalchemy](https://www.sqlalchemy.org/) | ORM and querying
| [Flask](https://flask.palletsprojects.com) | App server
| [Docker](https://www.docker.com/) | Containerization

## Setup

To query the Pot of Words database, it needs to be installed and accessed locally.

Start by cloning the repository and navigating to its root folder.

```shell
git clone https://github.com/vupdivup/pot-of-words.git
```

Build a Docker image for the project, then start a container.

```shell
docker build -t pot-of-words .
```

```shell
docker run -d -p 5000:5000 pot-of-words
```

The API will be accessible at http://localhost:5000.

### Without Docker

Alternatively, you can install the requirements and launch the Flask application manually.

```shell
pip install -r requirements.txt
```

```shell
flask --app src/app.py run
```

## Endpoints

### {host-url}/entries

Query all dictionary entries.

#### Parameters

- `key`: search expression for entry key, matches start of string
- `size`: number of entries to return, default: `32`, max: `128`
- `offset`: number of items to offset query by, useful for pagination

#### Example

Get entries starting with the letter `n`:

> http://localhost:5000/entries?key=n

```json
[
  {
    "id": 64821,
    "key": "n",
    "class": "n.",
    "pattern": "N",
    "etimology": null,
    "definitions": [
      "No, not. See No. [Obs.] Chaucer."
    ]
  },
  {
    "id": 64822,
    "key": "na",
    "class": "a.",
    "pattern": "Na",
    "etimology": null,
    "definitions": [
      "The summit of an eminence. [Prov. Eng.] Halliwell.",
      "The cock of a gunlock. Knight.",
      "The keeper, or box into which the lock is shot. Knight."
    ]
  },
  ...
```

### {host-url}/entries/{id}

Get a single dictionary entry based on its `id`.

#### Example

Get entry with `id` of 342:

> http://localhost:5000/entries/34

```json
{
  "id": 342,
  "key": "abridger",
  "class": "n.",
  "pattern": "A*bridg\"er",
  "etimology": null,
  "definitions": [
    "The act abridging, or the state of being abridged; diminution; lessening; reduction or deprivation; as, an abridgment of pleasures or of expenses.",
    "An epitome or compend, as of a book; a shortened or abridged form; an abbreviation. Ancient coins as abridgments of history. Addison.",
    "That which abridges or cuts short; hence, an entertainment that makes the time pass quickly. [Obs.] What abridgment have you for this evening What mask What music Shak. Syn."
  ]
}
```