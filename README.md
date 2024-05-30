# Getting started

## **Backend**

**Step 0:** Requirements

In our project we use: GIT, [Docker](https://docs.docker.com/desktop/windows/wsl/), Python 3.11.1 (Everything will be installed later)

If you use Windows — WSL 2 should be **[installed](https://learn.microsoft.com/en-us/windows/wsl/install)**.

1. Clone the backend project repository, switch to dev branch <br>
⚠️ Notice that we are currently developing at dev branch:
   ```bash
   git clone git@github.com:ur-abra-market/abra_back.git
   cd abra_back
   git switch dev
   ```


<br>

---

<br>

**Step 1**: Install project's dependencies

1. Install dependencies:
    ```bash
    sh ./scripts/dependency-installer.sh
    ```


<br>

---

<br>

**Step 2:** Build and Run the Docker Container

2.1 Copy `.env` [latest](https://t.me/c/1739270420/5100) file to the root of the project folder (you can find `.env` in
our chat, just look for the latest **#env** or **#backend**).

2.2 To start the project in Docker run:

```shell
make build  # Creating all docker images in the application
make migrations  # Creating tables in the database
make population  # Filling database
make application  # Launching application
```

2.3 You can find OpenAPI schema at http://localhost/docs

2.4 You can log in as a seller or a supplier with `supplier@gmail.ru` and `seller@gmail.ru` respectively. Password -
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
