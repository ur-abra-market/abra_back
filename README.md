# Getting started

## **Backend**

**Step 0:** Requirements

In our project we use: GIT, [Docker](https://docs.docker.com/desktop/windows/wsl/), Python 3.10.

If you use Windows — WSL 2 should be **[installed](https://learn.microsoft.com/en-us/windows/wsl/install)**.

Also needed:

1. Make tool

    ```bash
    sudo apt update && sudo apt-get -y install make
    ```

   For Windows users

   Install chocolatey from [here](https://chocolatey.org/install). Then run:

    ```shell
    choco install make
    ```

**Step 1**: Clone the backend project repository. Notice that we are currently developing at dev branch.

```bash
git clone git@github.com:ur-org/abra_back.git
cd abra_back
git switch dev
```

#### For backend

Do more step:

```bash
sh scripts/setup.sh  # or just copy all commands
```

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

To run the project locally:

```shell
python3 app/main.py
```

2.4 You can find OpenAPI schema at http://localhost/docs

2.5 You can log in as a seller or a supplier with `supplier@mail.ru` and `seller@mail.ru` respectively. Password -
`Password1!`

**Step 3:** Understand the architecture

3.1 You might be overwhelmed by the amount of custom elements in the project. But let me reassure you that it’s quite
easy to use once you get the gist.

3.2 SQLAlchemy models defined at `app/orm`. Notice that a lot of commonly used types are already defined:
`bool_true`, `decimal_10_2`, `moscow_datetime_timezone` etc. Feel free to add new.

3.3 Look at `app/core/app/crud/__init__.py`. It’s where main class for CRUD operations is defined:

```python
class _CRUD:
    admins: CRUD[AdminModel] = CRUD(AdminModel)
    categories: CRUD[CategoryModel] = CRUD(CategoryModel)
    companies: CRUD[CompanyModel] = CRUD(CompanyModel)
    ...
```

As you can see it contains all models. What is more it provides interface for all base SQL operations. You can find them
at `app/core/app/crud/operations`. It’s possible to do joins, grouping, ordering etc. just by passing args to functions:

```python
from corecrud import Limit, Offset, Options, OrderBy, Where
from core.app import crud
from orm import ProductModel, ProductPriceModel, SupplierModel

await crud.products.select.many(
    Where(
        ProductModel.is_active.is_(True),
        ProductModel.category_id == filters.category_id if filters.category_id else None,
    ),
    Options(
        selectinload(ProductModel.prices),
        selectinload(ProductModel.images),
        selectinload(ProductModel.supplier).joinedload(SupplierModel.user),
    ),
    Offset(pagination.offset),
    Limit(pagination.limit),
    OrderBy(filters.sort_type.by.asc() if filters.ascending else filters.sort_type.by.desc()),
    session=session,
)
```

3.4 We try to keep our code as much typed as possible. All inputs and outputs of any endpoint must be typed. You can
find schemas at app/schemas. Feel free to add new schemas but examine existing ones first.

3.5 All common functions (*auth*, *session*, *AWS interfaces*) are kept at app/core/depends. Before writing new piece of
code
make sure it has not been written yet ;)

********************Step 4:******************** Develop!

4.1 We use a bunch of code analysers. You can find full list at `.pre-commit-config.yaml`. They run automatically on
every
commit. Please notice that some of them (*black*, *isort*) can modify your code. If it is the case please run:

```shell
git add [filename]
```

again on the files that were changed.
