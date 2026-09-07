import {
  type Action,
  type FormResult,
  parseResult,
  type WorkerReply,
  type WorkerRequest,
} from './protocol.js';
import {
  type Draft,
  type Snapshot,
  StaleResetError,
  Store,
} from './storage.js';

interface Pending {
  resolve: (reply: Extract<WorkerReply, { ok: true }>) => void;
  reject: (error: Error) => void;
}

export class Client {
  public readonly store: Store = new Store();
  public epoch: string = '';
  private worker: Worker | null = null;
  private storageReady: boolean = false;
  private temporary: boolean = false;
  private nextId: number = 0;
  private pending: Map<number, Pending> = new Map();

  private stop(error: Error): void {
    this.worker?.terminate();
    this.worker = null;
    for (const pending of this.pending.values()) pending.reject(error);
    this.pending.clear();
  }

  private send(
    request:
      | Omit<Extract<WorkerRequest, { kind: 'dispatch' }>, 'id'>
      | { kind: 'start' },
  ): Promise<Extract<WorkerReply, { ok: true }>> {
    const worker: Worker | null = this.worker;
    if (!worker) return Promise.reject(new Error('Start the example first.'));
    const id: number = ++this.nextId;
    return new Promise((resolve, reject): void => {
      const timer: ReturnType<typeof setTimeout> = setTimeout(
        (): void => {
          this.stop(
            new Error('The Python worker timed out. Retry to continue.'),
          );
        },
        request.kind === 'start' ? 150_000 : 30_000,
      );
      this.pending.set(id, {
        resolve: (reply): void => {
          clearTimeout(timer);
          resolve(reply);
        },
        reject: (error): void => {
          clearTimeout(timer);
          reject(error);
        },
      });
      try {
        worker.postMessage({ ...request, id });
      } catch (error: unknown) {
        this.stop(error instanceof Error ? error : new Error(String(error)));
      }
    });
  }

  async start(temporary: boolean = this.temporary): Promise<void> {
    this.stop(new Error('The example is restarting.'));
    if (!this.storageReady || temporary !== this.temporary) {
      if (temporary) this.store.useTemporary();
      else await this.store.open();
      this.temporary = temporary;
      this.storageReady = true;
    }
    this.worker = new Worker(new URL('worker.js', import.meta.url), {
      type: 'module',
    });
    this.worker.onmessage = (event: MessageEvent<WorkerReply>): void => {
      const pending: Pending | undefined = this.pending.get(event.data.id);
      if (!pending) return;
      this.pending.delete(event.data.id);
      if (event.data.ok) pending.resolve(event.data);
      else pending.reject(new Error(event.data.error));
    };
    this.worker.onerror = (): void => {
      this.stop(new Error('The Python worker stopped. Retry to continue.'));
    };
    try {
      await this.send({ kind: 'start' });
    } catch (error: unknown) {
      this.stop(error instanceof Error ? error : new Error(String(error)));
      throw error;
    }
  }

  async dispatch(payload: Action): Promise<FormResult | string[]> {
    return this.store.locked(async (): Promise<FormResult | string[]> => {
      let snapshot: Snapshot;
      if (payload.action === 'reset') snapshot = await this.store.reset();
      else snapshot = await this.store.read();
      if (payload.action === 'save' && this.epoch !== snapshot.epoch)
        throw new StaleResetError();
      const reply: Extract<WorkerReply, { ok: true }> = await this.send({
        kind: 'dispatch',
        payload,
        database: snapshot.database,
      });
      const result: FormResult | string[] = parseResult(reply.result);
      if (payload.action !== 'suggest') {
        snapshot.database = reply.database;
        if (
          payload.action === 'save' &&
          !Array.isArray(result) &&
          Object.keys(result.errors).length === 0
        )
          delete snapshot.drafts[payload.mode];
        await this.store.write(snapshot);
        this.epoch = snapshot.epoch;
      }
      return result;
    });
  }

  async draft(mode: Action['mode']): Promise<Draft | undefined> {
    return this.store.locked(async (): Promise<Draft | undefined> => {
      const snapshot: Snapshot = await this.store.read();
      return snapshot.drafts[mode];
    });
  }
}
