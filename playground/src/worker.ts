import {
  parseResult,
  type WorkerReply,
  type WorkerRequest,
} from './protocol.js';

interface PythonRuntime {
  FS: {
    writeFile(path: string, data: Uint8Array): void;
    readFile(path: string): Uint8Array;
  };
  globals: { set(name: string, value: string): void };
  loadPackage(name: string): Promise<void>;
  runPythonAsync(code: string): Promise<unknown>;
}

interface Wheel {
  url: string;
  sha256: string;
}

interface Manifest {
  pyodide: string;
  wheels: Wheel[];
  sources: Record<string, string>;
  versions: Record<string, string>;
}

function stringMap(value: unknown): value is Record<string, string> {
  return (
    typeof value === 'object' &&
    value !== null &&
    !Array.isArray(value) &&
    Object.values(value).every(
      (item: unknown): boolean => typeof item === 'string',
    )
  );
}

function parseManifest(value: unknown): Manifest {
  if (typeof value !== 'object' || value === null)
    throw new Error('Invalid example manifest.');
  const item: Record<string, unknown> = value as Record<string, unknown>;
  if (
    typeof item.pyodide !== 'string' ||
    !/^https:\/\/cdn\.jsdelivr\.net\/pyodide\/v[0-9.]+\/full\/pyodide\.mjs$/.test(
      item.pyodide,
    ) ||
    !Array.isArray(item.wheels) ||
    !item.wheels.length ||
    !item.wheels.every((wheel: unknown): boolean => {
      if (typeof wheel !== 'object' || wheel === null) return false;
      const entry: Record<string, unknown> = wheel as Record<string, unknown>;
      return (
        typeof entry.url === 'string' &&
        /^wheels\/[A-Za-z0-9_.+-]+\.whl$/.test(entry.url) &&
        typeof entry.sha256 === 'string' &&
        /^[a-f0-9]{64}$/.test(entry.sha256)
      );
    }) ||
    !stringMap(item.sources) ||
    !Object.keys(item.sources).every(
      (path: string): boolean =>
        /^[A-Za-z0-9_/-]+\.(py|html)$/.test(path) && !path.startsWith('/'),
    ) ||
    !stringMap(item.versions) ||
    !Object.keys(item.versions).length
  ) {
    throw new Error('Invalid example manifest.');
  }
  return item as unknown as Manifest;
}

let python: PythonRuntime | null = null;
let queue: Promise<void> = Promise.resolve();
const DATABASE: string = '/showcase.sqlite3';

async function checkedBytes(
  url: string,
  expected: string,
): Promise<Uint8Array> {
  const response: Response = await fetch(new URL(url, import.meta.url));
  if (!response.ok)
    throw new Error(`Could not download ${url}: ${response.status}`);
  const bytes: ArrayBuffer = await response.arrayBuffer();
  const digest: ArrayBuffer = await crypto.subtle.digest('SHA-256', bytes);
  const actual: string = Array.from(
    new Uint8Array(digest),
    (value: number): string => value.toString(16).padStart(2, '0'),
  ).join('');
  if (actual !== expected) throw new Error(`Checksum mismatch for ${url}`);
  return new Uint8Array(bytes);
}

async function start(): Promise<PythonRuntime> {
  if (python) return python;
  const response: Response = await fetch(
    new URL('manifest.json', import.meta.url),
  );
  if (!response.ok)
    throw new Error('The example manifest could not be loaded.');
  const manifest: Manifest = parseManifest(await response.json());
  const loader: {
    loadPyodide(options: { indexURL: string }): Promise<PythonRuntime>;
  } = await import(manifest.pyodide);
  const runtime: PythonRuntime = await loader.loadPyodide({
    indexURL: new URL('.', manifest.pyodide).href,
  });
  await runtime.loadPackage('micropip');
  const wheels: string[] = [];
  for (const wheel of manifest.wheels) {
    const filename: string | undefined = wheel.url.split('/').pop();
    if (!filename?.endsWith('.whl')) throw new Error('Invalid wheel filename.');
    const path: string = `/tmp/${filename}`;
    runtime.FS.writeFile(path, await checkedBytes(wheel.url, wheel.sha256));
    wheels.push(`emfs:${path}`);
  }
  runtime.globals.set('_showcase_wheels', JSON.stringify(wheels));
  runtime.globals.set('_showcase_sources', JSON.stringify(manifest.sources));
  runtime.globals.set('_showcase_versions', JSON.stringify(manifest.versions));
  await runtime.runPythonAsync(`
import json, os, pathlib, sys
import micropip
await micropip.install(json.loads(_showcase_wheels), deps=False)
from importlib.metadata import version
for name, expected in json.loads(_showcase_versions).items():
    assert version(name) == expected, f'{name}: expected {expected}, got {version(name)}'
for name, source in json.loads(_showcase_sources).items():
    path = pathlib.Path('/home/pyodide') / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source)
os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
from showcase.runtime import initialise, dispatch_json
initialise('/showcase.sqlite3')
`);
  python = runtime;
  return runtime;
}

async function handle(message: WorkerRequest): Promise<void> {
  try {
    const runtime: PythonRuntime = await start();
    if (message.kind !== 'dispatch') {
      postMessage({
        id: message.id,
        ok: true,
        result: null,
        database: null,
      } satisfies WorkerReply);
      return;
    }
    await runtime.runPythonAsync(
      'from django.db import connections\nconnections.close_all()',
    );
    if (message.database) runtime.FS.writeFile(DATABASE, message.database);
    else
      await runtime.runPythonAsync(
        "pathlib.Path('/showcase.sqlite3').unlink(missing_ok=True)\ninitialise('/showcase.sqlite3')",
      );
    runtime.globals.set('_showcase_request', JSON.stringify(message.payload));
    const output: unknown = await runtime.runPythonAsync(
      'dispatch_json(_showcase_request)',
    );
    if (typeof output !== 'string')
      throw new Error('Django returned an invalid response.');
    const result: ReturnType<typeof parseResult> = parseResult(
      JSON.parse(output) as unknown,
    );
    await runtime.runPythonAsync('connections.close_all()');
    const database: Uint8Array = runtime.FS.readFile(DATABASE);
    postMessage({
      id: message.id,
      ok: true,
      result,
      database,
    } satisfies WorkerReply);
  } catch (error: unknown) {
    postMessage({
      id: message.id,
      ok: false,
      error: error instanceof Error ? error.message : String(error),
    } satisfies WorkerReply);
  }
}

addEventListener('message', (event: MessageEvent<WorkerRequest>): void => {
  queue = queue.then(async (): Promise<void> => handle(event.data));
});
