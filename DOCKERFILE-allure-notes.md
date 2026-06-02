# Dockerfile additions for Allure reporting

The `005_reporting` example (and the `task report` target) build an Allure HTML
report. This needs **two** things in the container that the Python deps alone do
not provide:

1. A **Java runtime (JRE)** — the Allure CLI is a JVM tool.
2. The **Allure CLI** binary itself — it is *not* a pip package.

The Python side (`allure-pytest`) is already handled: it is listed in
`pyproject.toml` and installed by `uv sync`, so it produces the raw
`allure-results/*.json`. The CLI is only what turns that JSON into HTML.

## Add this to the Dockerfile (Debian/Ubuntu base)

```dockerfile
# --- Allure reporting: JRE + Allure CLI -------------------------------------
ARG ALLURE_VERSION=2.42.0

RUN apt-get update && apt-get install -y --no-install-recommends \
        default-jre-headless \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL -o /tmp/allure.tgz \
      "https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.tgz" \
    && tar -xzf /tmp/allure.tgz -C /opt \
    && ln -s "/opt/allure-${ALLURE_VERSION}/bin/allure" /usr/local/bin/allure \
    && rm /tmp/allure.tgz \
    && allure --version
# ---------------------------------------------------------------------------
```

## Notes

- `ALLURE_VERSION=2.42.0` matches the version used locally. Bump the ARG to
  upgrade; nothing else changes.
- Use `default-jre-headless` (not the full JRE) — no GUI is needed and it keeps
  the image smaller.
- `npm install -g allure-commandline` is an alternative, but it pulls in Node
  *and* still needs a JRE, so the tarball approach above is lighter.
- Inside the container, generate a self-contained report with:
  ```bash
  uv run pytest 003_pytest/005_reporting --alluredir=allure-results
  allure generate allure-results -o allure-report --single-file --clean
  ```
  or just `task report`.
- `allure serve` tries to auto-open a browser and will fail headless
  (`BROWSE action is not supported`). In a container always use
  `allure generate ... --single-file` and copy/serve the static HTML instead.
