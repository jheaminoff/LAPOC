const DB_NAME = 'lapoc-audio-cache'
const STORE_NAME = 'synthesized'

function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, 1)
    req.onupgradeneeded = () => req.result.createObjectStore(STORE_NAME)
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(new Error(req.error?.message ?? 'Failed to open audio cache'))
  })
}

export async function getCachedAudio(key: string): Promise<ArrayBuffer[] | null> {
  const db = await openDB()
  return new Promise<ArrayBuffer[] | null>((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readonly')
    const req = tx.objectStore(STORE_NAME).get(key)
    req.onsuccess = () => resolve((req.result as ArrayBuffer[] | undefined) ?? null)
    req.onerror = () => reject(new Error(req.error?.message ?? 'Failed to read audio cache'))
  })
}

export async function setCachedAudio(key: string, chunks: ArrayBuffer[]): Promise<void> {
  const db = await openDB()
  return new Promise<void>((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite')
    tx.objectStore(STORE_NAME).put(chunks, key)
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(new Error(tx.error?.message ?? 'Failed to write audio cache'))
  })
}
