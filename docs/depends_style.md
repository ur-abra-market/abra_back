# Depends

For our dependencies we use the style through `typing_extensions.Annotated`, previously we
used: `session: AsyncSession = Depends(get_session)` for the database dependency, and now we
use `session: DatabaseSession`, similarly for authorization: `user: Authorization`,
all dependencies are defined in `app.core.depends`.
