'use client'

interface StoreSelectorProps {
  selectedStore: string
  onStoreChange: (store: string) => void
}

const STORES = [
  { id: 'store-1', name: 'Sucursal Centro' },
  { id: 'store-2', name: 'Sucursal Norte' },
  { id: 'store-3', name: 'Sucursal Sur' },
]

export default function StoreSelector({
  selectedStore,
  onStoreChange,
}: StoreSelectorProps) {
  return (
    <div className="flex items-center gap-2">
      <label htmlFor="store" className="text-sm font-medium text-gray-700">
        Sucursal:
      </label>
      <select
        id="store"
        value={selectedStore}
        onChange={(e) => onStoreChange(e.target.value)}
        className="px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white"
      >
        {STORES.map((store) => (
          <option key={store.id} value={store.id}>
            {store.name}
          </option>
        ))}
      </select>
    </div>
  )
}

