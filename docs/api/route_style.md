All arguments when we specify, for example, `@router.get` - we pass them by name. The first thing we pass is `path`,
which is usually a singular noun or Past Simple verb and must end with `/` and begin with it. Next, we make sure to
specify `summary` (for workers, the first place is "WORKS"), which describes how the route works. Then `response_model`,
we have `ApplicationResponse` everywhere, in which you pass your schema or a built-in Python type, such
as `ApplicationSchema[bool]`. The last mandatory parameter is `status_code`, in which you specify the response code that
returns the route, for successful ones, `starlette.HTTP_200_OK`. All other arguments you don't have to pass.
