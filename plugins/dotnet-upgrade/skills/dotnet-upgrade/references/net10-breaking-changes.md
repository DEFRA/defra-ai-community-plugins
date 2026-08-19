# .NET 10 — General Breaking Changes & Runtime Notes

> Reference: https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-10/overview

## Runtime & SDK

- Minimum SDK: `10.0.100`
- LTS release: .NET 10 is an LTS (Long-Term Support) release.
- C# version: C# 14 is the default with .NET 10 SDK.

## System.Text.Json

- Source generation is stricter — all polymorphic serialization requires `[JsonDerivedType]`.
- `JsonSerializerOptions.Default` is now truly read-only at runtime.
- `Utf8JsonReader` / `Utf8JsonWriter`: no breaking changes.

## LINQ

- `CountBy`, `AggregateBy`, `Index` extension methods added (from .NET 9) — no breaking changes.

## Reflection

- `Type.GetMethod()` with ambiguous matches now throws in more cases — be explicit with binding flags.

## Threading

- `Thread.CurrentThread.Name` is settable only once (was already the case, enforced stricter).
- `TimeProvider` is stable — replace `DateTime.UtcNow` usages where testability matters.

## Removed APIs

| API | Replacement |
|---|---|
| `BinaryFormatter` | `System.Text.Json` or `System.Runtime.Serialization` |
| `Hashtable` (in new code) | `Dictionary<TKey, TValue>` |
| Obsolete `WebClient` | `HttpClient` |
| `Newtonsoft.Json` (not removed, but migrate) | `System.Text.Json` |

## NuGet Package Compatibility

- Packages targeting `netstandard2.0` or `netstandard2.1` continue to work on net10.0.
- Packages targeting `net8.0` specifically: check for `net10.0` or `net9.0` TFM support.
- Use `dotnet list package --outdated` and `dotnet list package --vulnerable` after upgrade.