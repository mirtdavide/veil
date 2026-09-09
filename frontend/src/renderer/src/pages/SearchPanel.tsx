import { useState } from 'react'

interface SearchResult {
  id: number
  username: string
}

const searchResults: SearchResult[] = [
  { id: 1, username: 'ilpelato' },
  { id: 2, username: 'gheia' },
  { id: 3, username: 'omgitsandre' }
]

interface SearchPanelProps {
  onSendRequest: (userId: number) => void
}

function SearchPanel({ onSendRequest }: SearchPanelProps): React.JSX.Element {
  const [query, setQuery] = useState('')

  const filteredResults = searchResults.filter((result) =>
    result.username.toLowerCase().includes(query.toLowerCase())
  )

  return (
    <div className="flex-1 bg-bg h-screen flex flex-col p-4 gap-3">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Cerca per username"
        className="bg-bg-tertiary text-text placeholder-text-muted rounded px-3 py-2 outline-none"
      />
      <div className="flex flex-col gap-2">
        {filteredResults.map((result) => (
          <div
            key={result.id}
            className="flex items-center justify-between px-3 py-2 bg-bg-secondary rounded"
          >
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-bg-tertiary flex items-center justify-center text-text font-semibold text-sm">
                {result.username.charAt(0).toUpperCase()}
              </div>
              <p className="text-text">{result.username}</p>
            </div>
            <button
              onClick={() => onSendRequest(result.id)}
              className="bg-accent hover:bg-accent-hover text-text text-sm rounded px-3 py-1"
            >
              Aggiungi
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

export default SearchPanel