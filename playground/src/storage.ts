import { isMode, type Mode } from './protocol.js';

const NAME: string = 'django-tags-input-showcase';
const SCHEMA: number = 1;
const LOCK: string = `${NAME}:write`;

export interface Draft {
  tags: string;
  incomplete: string;
}

export interface Snapshot {
  schema: number;
  epoch: string;
  database: Uint8Array | null;
  drafts: Partial<Record<Mode, Draft>>;
}

export class StaleResetError extends Error {
  constructor() {
    super(
      'This example was reset in another tab. Reload the example before saving.',
    );
  }
}

function empty(): Snapshot {
  return {
    schema: SCHEMA,
    epoch: crypto.randomUUID(),
    database: null,
    drafts: {},
  };
}

function isDraft(value: unknown): value is Draft {
  return (
    typeof value === 'object' &&
    value !== null &&
    'tags' in value &&
    typeof value.tags === 'string' &&
    'incomplete' in value &&
    typeof value.incomplete === 'string'
  );
}

function validate(value: unknown): Snapshot {
  if (typeof value !== 'object' || value === null)
    throw new Error('Stored example data is invalid. Reset to start again.');
  const item: Record<string, unknown> = value as Record<string, unknown>;
  if (
    item.schema !== SCHEMA ||
    typeof item.epoch !== 'string' ||
    !(item.database === null || item.database instanceof Uint8Array) ||
    typeof item.drafts !== 'object' ||
    item.drafts === null ||
    !Object.entries(item.drafts).every(
      ([key, draft]: [string, unknown]): boolean =>
        isMode(key) && isDraft(draft),
    )
  ) {
    throw new Error(
      'Stored example data uses an incompatible format. Reset to start again.',
    );
  }
  return item as unknown as Snapshot;
}

function request<T>(operation: IDBRequest<T>): Promise<T> {
  return new Promise<T>(
    (resolve: (value: T) => void, reject: (error: unknown) => void): void => {
      operation.onsuccess = (): void => resolve(operation.result);
      operation.onerror = (): void =>
        reject(operation.error ?? new Error('Browser storage failed.'));
    },
  );
}

export class Store {
  private database: IDBDatabase | null = null;
  private temporary: Snapshot = empty();
  private temporaryQueue: Promise<unknown> = Promise.resolve();
  public persistent: boolean = false;

  close(): void {
    this.database?.close();
    this.database = null;
    this.persistent = false;
  }

  async open(): Promise<void> {
    this.close();
    if (!navigator.locks)
      throw new Error(
        'Web Locks are unavailable. Choose temporary mode to continue.',
      );
    const operation: IDBOpenDBRequest = indexedDB.open(NAME, SCHEMA);
    operation.onupgradeneeded = (): void => {
      operation.result.createObjectStore('state');
    };
    this.database = await new Promise<IDBDatabase>((resolve, reject): void => {
      let settled: boolean = false;
      const timer: ReturnType<typeof setTimeout> = setTimeout((): void => {
        settled = true;
        reject(
          new Error(
            'Browser storage timed out. Choose temporary mode to continue.',
          ),
        );
      }, 10_000);
      operation.onsuccess = (): void => {
        clearTimeout(timer);
        if (settled) operation.result.close();
        else {
          settled = true;
          resolve(operation.result);
        }
      };
      const fail: () => void = (): void => {
        clearTimeout(timer);
        settled = true;
        reject(
          operation.error ??
            new Error(
              'Browser storage is blocked. Choose temporary mode to continue.',
            ),
        );
      };
      operation.onerror = fail;
      operation.onblocked = fail;
    });
    this.database.onversionchange = (): void => this.database?.close();
    this.persistent = true;
  }

  useTemporary(): void {
    this.close();
    this.temporary = empty();
  }

  async locked<T>(operation: () => Promise<T>): Promise<T> {
    if (!this.persistent) {
      const result: Promise<T> = this.temporaryQueue.then(operation);
      this.temporaryQueue = result.catch((): void => {});
      return result;
    }
    return navigator.locks.request(LOCK, operation);
  }

  async read(): Promise<Snapshot> {
    if (!this.database) return structuredClone(this.temporary);
    const value: unknown = await request(
      this.database.transaction('state').objectStore('state').get('current'),
    );
    if (value === undefined) {
      const initial: Snapshot = empty();
      await this.write(initial);
      return initial;
    }
    return validate(value);
  }

  async write(snapshot: Snapshot): Promise<void> {
    if (!this.database) {
      this.temporary = structuredClone(snapshot);
      return;
    }
    const transaction: IDBTransaction = this.database.transaction(
      'state',
      'readwrite',
    );
    const complete: Promise<void> = new Promise<void>(
      (resolve: () => void, reject: (error: unknown) => void): void => {
        transaction.oncomplete = (): void => resolve();
        transaction.onerror = (): void =>
          reject(
            transaction.error ?? new Error('Could not save browser data.'),
          );
        transaction.onabort = (): void =>
          reject(
            transaction.error ??
              new Error('Browser storage transaction was cancelled.'),
          );
      },
    );
    transaction.objectStore('state').put(snapshot, 'current');
    await complete;
  }

  async reset(): Promise<Snapshot> {
    const snapshot: Snapshot = empty();
    await this.write(snapshot);
    return snapshot;
  }

  async draft(mode: Mode, value: Draft, epoch: string): Promise<void> {
    await this.locked(async (): Promise<void> => {
      const snapshot: Snapshot = await this.read();
      if (snapshot.epoch !== epoch) throw new StaleResetError();
      snapshot.drafts[mode] = value;
      await this.write(snapshot);
    });
  }
}
