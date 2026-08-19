# .NET 10 — ASP.NET Core Breaking Changes & Migration Notes

> Reference: https://learn.microsoft.com/en-us/aspnet/core/migration/80-to-10

## OpenAPI / Swagger

- **Swashbuckle.AspNetCore** is no longer the default in ASP.NET Core templates from .NET 9+.
- Built-in OpenAPI support: `Microsoft.AspNetCore.OpenApi` is the recommended replacement.
- Migration:
  ```csharp
  // Remove:
  builder.Services.AddSwaggerGen();
  app.UseSwagger();
  app.UseSwaggerUI();

  // Add:
  builder.Services.AddOpenApi();
  app.MapOpenApi();
  ```
- If Swashbuckle must be kept, ensure version 7.x+ for .NET 9/10 compatibility.

## Authentication & Authorization

- `JwtBearer` package: use `Microsoft.AspNetCore.Authentication.JwtBearer` 10.x.
- No breaking changes in JWT validation pipeline from .NET 8 → 10.
- `AddAuthorizationBuilder()` is the preferred API (available since .NET 8, no change).

## Minimal APIs

- `IResult` implementations are sealed — avoid inheriting from built-in result types.
- `TypedResults` static class remains stable.

## Model Binding

- `[FromServices]` implicit injection for action parameters: behaviour unchanged.
- `[AsParameters]` record binding: unchanged.

## Entity Framework Core

- Update all `Microsoft.EntityFrameworkCore.*` packages to 10.x.
- `UseQuerySplittingBehavior` default unchanged.
- `ExecuteUpdate` / `ExecuteDelete`: stable API.

## Kestrel

- `KestrelServerOptions.Limits` unchanged.
- HTTP/3 support: ensure `Microsoft.AspNetCore.Server.Kestrel.Transport.Quic` is referenced
  if HTTP/3 is enabled.

## Health Checks

- No breaking changes in `Microsoft.Extensions.Diagnostics.HealthChecks`.

## Nullable Reference Types

- Consider enabling `<Nullable>enable</Nullable>` during upgrade — not mandatory but recommended.

## Removed / Obsolete APIs

| API | Replacement |
|---|---|
| `IWebHostBuilder.Configure(Action<IApplicationBuilder>)` | Use `WebApplication` builder pattern |
| `WebHost.CreateDefaultBuilder()` (legacy) | Use `WebApplication.CreateBuilder()` |
| `app.UseRouting()` before `app.UseEndpoints()` explicit pattern | Still works but not required with minimal APIs |