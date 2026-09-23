import { useState, useEffect } from 'react'

interface SearchResult {
  id: number
  username: string
}

interface SentRequest {
  id: number
  addressee: {
    id: number
    username: string
  }
  status: string
  created_at: string
}

interface SearchPanelProps {
  accessToken: string | null
  onViewProfile: (userId: number) => void
}

function SearchPanel({ accessToken, onViewProfile }: SearchPanelProps): React.JSX.Element {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [sentRequests, setSentRequests] = useState<SentRequest[]>([])
  const [error, setError] = useState<string | null>(null)

  async function loadSentRequests(): Promise<void> {
    const response = await fetch('http://127.0.0.1:8000/connections/sent', {
      headers: { Authorization: `Bearer ${accessToken}` }
    })

    if (!response.ok) {
      console.log('errore caricamento richieste inviate', response.status)
      return
    }

    const data = await response.json()
    setSentRequests(data)
  }

  useEffect(() => {
    loadSentRequests()
  }, [])

  useEffect(() => {
    async function searchUsers(): Promise<void> {
      if (query.trim() === '') {
        setResults([])
        return
      }

      const response = await fetch(
        `http://127.0.0.1:8000/connections/search?q=${encodeURIComponent(query)}`,
        { headers: { Authorization: `Bearer ${accessToken}` } }
      )

      if (!response.ok) {
        console.log('errore ricerca utenti', response.status)
        return
      }

      const data = await response.json()
      setResults(data)
    }

    searchUsers()
  }, [query])

  async function handleSendRequest(userId: number): Promise<void> {
    const response = await fetch('http://127.0.0.1:8000/connections', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`
      },
      body: JSON.stringify({ addressee_id: userId })
    })

    if (!response.ok) {
      const data = await response.json()
      setError(data.detail ?? 'Invio della richiesta fallito')
      setTimeout(() => setError(null), 4000)
      return
    }

    setError(null)
    loadSentRequests()
  }

  function statusLabel(status: string): string {
    if (status === 'accepted') return 'Accettata'
    return 'In attesa'
  }

  return (
    <div className="flex-1 bg-bg h-screen flex flex-col p-4 gap-4 overflow-y-auto">
      <div className="flex flex-col gap-3">
        <p className="text-text font-semibold">Cerca amici</p>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Cerca per username"
          className="bg-bg-tertiary text-text placeholder-text-muted rounded px-3 py-2 outline-none"
        />
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <div className="flex flex-col gap-2">
          {results.map((result) => {
            const alreadySent = sentRequests.find((r) => r.addressee.id === result.id)
            return (
              <div
                key={result.id}
                className="flex items-center justify-between px-3 py-2 bg-bg-secondary rounded"
              >
                <div className="flex items-center gap-3">
                  <div
                    onClick={() => onViewProfile(result.id)}
                    className="w-9 h-9 rounded-full bg-bg-tertiary flex items-center justify-center text-text font-semibold text-sm cursor-pointer"
                  >
                    {result.username.charAt(0).toUpperCase()}
                  </div>
                  <p className="text-text">{result.username}</p>
                </div>
                {alreadySent ? (
                  <span className="text-text-muted text-sm px-3 py-1">
                    {statusLabel(alreadySent.status)}
                  </span>
                ) : (
                  <button
                    onClick={() => handleSendRequest(result.id)}
                    className="bg-accent hover:bg-accent-hover text-text text-sm rounded px-3 py-1"
                  >
                    Aggiungi
                  </button>
                )}
              </div>
            )
          })}
        </div>
      </div>

      <div className="flex flex-col gap-3 border-t border-bg-tertiary pt-4">
        <p className="text-text font-semibold">Richieste inviate</p>
        <div className="flex flex-col gap-2">
          {sentRequests.length === 0 && (
            <p className="text-text-muted text-sm">Nessuna richiesta inviata</p>
          )}
          {sentRequests.map((request) => (
            <div
              key={request.id}
              className="flex items-center justify-between px-3 py-2 bg-bg-secondary rounded"
            >
              <div className="flex items-center gap-3">
                <div
                  onClick={() => onViewProfile(request.addressee.id)}
                  className="w-9 h-9 rounded-full bg-bg-tertiary flex items-center justify-center text-text font-semibold text-sm cursor-pointer"
                >
                  {request.addressee.username.charAt(0).toUpperCase()}
                </div>
                <p className="text-text">{request.addressee.username}</p>
              </div>
              <span className="text-text-muted text-sm px-3 py-1">
                {statusLabel(request.status)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default SearchPanel
