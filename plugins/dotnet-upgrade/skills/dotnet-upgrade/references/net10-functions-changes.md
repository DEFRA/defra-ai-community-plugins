# .NET 10 — Azure Functions Isolated Worker Breaking Changes & Migration Notes

> Reference: https://learn.microsoft.com/en-us/azure/azure-functions/dotnet-isolated-process-guide

## Supported Runtime

- Azure Functions v4 runtime supports .NET 10 isolated worker.
- **Isolated worker model is required** — in-process model does not support .NET 10.

## Package Versions (net10.0 compatible)

| Package                                                       | Minimum Version |
| ------------------------------------------------------------- | --------------- |
| `Microsoft.Azure.Functions.Worker`                            | 2.0.0           |
| `Microsoft.Azure.Functions.Worker.Sdk`                        | 2.0.0           |
| `Microsoft.Azure.Functions.Worker.Extensions.Http`            | 3.2.0           |
| `Microsoft.Azure.Functions.Worker.Extensions.Http.AspNetCore` | 2.0.0           |
| `Microsoft.Azure.Functions.Worker.Extensions.ServiceBus`      | 5.x             |
| `Microsoft.Azure.Functions.Worker.Extensions.Storage`         | 6.x             |
| `Microsoft.Azure.Functions.Worker.Extensions.Timer`           | 4.x             |
| `Microsoft.Azure.Functions.Worker.Extensions.EventHubs`       | 6.x             |
| `Microsoft.Azure.Functions.Worker.Extensions.CosmosDB`        | 4.x             |

## host.json — Extension Bundle

Update to bundle v4 (required for .NET 10):

```json
{
  "version": "2.0",
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  }
}
```

## Program.cs — Host Builder Pattern

Standard pattern (unchanged from .NET 8, verify it matches):

```csharp
var host = new HostBuilder()
    .ConfigureFunctionsWorkerDefaults()
    .ConfigureServices(services =>
    {
        // your DI registrations
    })
    .Build();

await host.RunAsync();
```

With ASP.NET Core integration (recommended for HTTP triggers):

```csharp
var host = new HostBuilder()
    .ConfigureFunctionsWebApplication()
    .ConfigureServices(services =>
    {
        services.AddApplicationInsightsTelemetryWorkerService();
        services.ConfigureFunctionsApplicationInsights();
    })
    .Build();

await host.RunAsync();
```

## Middleware

- `IFunctionsWorkerMiddleware` interface: unchanged.
- Register via `.UseMiddleware<T>()` on `ConfigureFunctionsWorkerDefaults`.

## HTTP Trigger Changes

- Use `HttpRequestData` / `HttpResponseData` (isolated) — not `HttpRequest` / `IActionResult`.
- If `ConfigureFunctionsWebApplication()` is used, `HttpRequest` / `IActionResult` are available.

## Dependency Injection

- Full `IServiceCollection` DI available — unchanged from .NET 8.
- `IConfiguration` / `IOptions<T>` patterns: unchanged.

## Breaking Changes .NET 8 → .NET 10

| Area                                       | Change                                                  |
| ------------------------------------------ | ------------------------------------------------------- |
| `System.Text.Json` source gen              | Stricter — ensure `JsonSerializerContext` is registered |
| `CancellationToken` in function signatures | Now preferred over `FunctionContext` cancellation       |
| `ILogger<T>` injection                     | Preferred over `ILogger` from `FunctionContext`         |

## Local Development

- Install Azure Functions Core Tools v4.x.
- `func start` works with net10.0 isolated worker.
- Ensure `local.settings.json` has `"FUNCTIONS_WORKER_RUNTIME": "dotnet-isolated"`.
