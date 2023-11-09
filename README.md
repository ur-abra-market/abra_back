# Getting started

## **Backend**

**Step 0:** Requirements

In our project we use: GIT, [Docker](https://docs.docker.com/desktop/windows/wsl/), Python 3.11.1

If you use Windows — WSL 2 should be **[installed](https://learn.microsoft.com/en-us/windows/wsl/install)**.

Also needed:

1. Update your packages with:
    ```bash
    sudo apt update && sudo apt-get upgrade -y
    ```

1. Install Make tool:

    For linux/macos users:
    ```bash
    sudo apt-get -y install make
    ```

   For Windows users:

   - Install chocolatey from [here](https://chocolatey.org/install). Then run:

    ```shell
    choco install make
    ```

<br>

---

<br>

**Step 1**: Clone the backend project repository, switch to dev branch: <br>
⚠️ Notice that we are currently developing at dev branch.

```bash
git clone git@github.com:ur-abra-market/abra_back.git
cd abra_back
git switch dev
```

#### ❗️ For backend only

- Make sure you have Poetry installed:

```bash
pip install -U pip
poetry config virtualenvs.in-project true
pip install poetry
```

- Install the project dependencies:

```bash
poetry install
poetry shell
pre-commit install
exit
```

<br>

---

<br>

**Step 2:** Build and Run the Docker Container

2.1. Copy `.env` [latest](https://t.me/c/1739270420/5100) file to the root of the project folder (you can find `.env` in
our chat, just look for the latest **#env** or **#backend**).

2.2. To start the project in Docker run:

```shell
make build
make migrations
make population
make application
```

To start the project **locally**:

```shell
python3 app/main.py
```

2.4 You can find OpenAPI schema at http://localhost/docs

2.5 You can log in as a seller or a supplier with `supplier@gmail.ru` and `seller@gmail.ru` respectively. Password -
`Password1!`

<br>

---

<br>

**Step 3:** Understand the architecture

3.1 You might be overwhelmed by the amount of custom elements in the project. But let me reassure you that it’s quite
easy to use once you get the gist.

3.2 SQLAlchemy models defined at `app/orm`. Notice that a lot of commonly used types are already defined:
`bool_true`, `decimal_10_2` etc. Feel free to add new.

3.3 We try to keep our code as much typed as possible. All inputs and outputs of any endpoint must be typed. You can
find schemas at app/schemas. Feel free to add new schemas but examine existing ones first.

3.4 All common functions (*auth*, *session*, *AWS interfaces*) are kept at app/core/depends. Before writing new piece of
code
make sure it has not been written yet 😉

<br>

---

<br>

**Step 4:** Develop!

4.1 We use a bunch of code analysers. You can find full list at `.pre-commit-config.yaml`. They run automatically on
every
commit. Please notice that some of them (*black*, *isort*) can modify your code. If it is the case please run:

```shell
git add .
```

again on the files that were changed.
