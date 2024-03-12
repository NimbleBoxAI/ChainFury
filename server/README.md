# ChainFury Server

This is a package separate from `chainfury` which provides the python execution engine.

## .env file

Create the following file and pass the `CFS_DOTENV` env var

```bash
# Environment variables.

# If passed this is taken by the sqlalchemy.create_engine function
# by default it None and creates a local sqlite DB.
CFS_DATABASE='<database-path>'

# configurations
JWT_SECRET="hajime-shimamoto"     # default, Murakami <3
CFS_MAXLEN_CF_NDOE=80             # maximum length of the chainfury node ID
CFS_MAXLEN_WORKER=16              # length of the worker ID
CFS_ALLOW_CORS_ORIGINS='*'        # or pass with , split like xxx,yyy
CFS_ALLOW_METHODS='*'             # or pass with , split like xxx,yyy
CFS_ALLOW_HEADERS='*'             # or pass with , split like xxx,yyy
CFS_DISABLE_UI=0                  # set 1 to disable UI
CFS_DISABLE_DOCS=0                # set 0 to disable swagger
```
